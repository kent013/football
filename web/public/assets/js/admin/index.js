var zoom;
var svg;
$(document).ready(() => {
  var graph_schema = {};
  function loadSchema() {
    var promise = $.ajax({
      method: 'GET',
      url: "/assets/js/admin/schema.json",
    });
    return promise.done((data) => {
      graph_schema = data;
    });
  }
  loadSchema();

  $("#subject_token").select2({
    placeholder: 'subject Token',
    ajax: {
      url: "/admin/tokens",
      dataType: 'json',
      delay: 250,
      minimumInputLength: 1,
      allowClear: true,

      data: (params) => {
        var is_noise = $('input[name=subject_token_is_noise]:checked').val();
        if (is_noise == "include") {
          params.is_noise = 1;
        } else if (is_noise == "exclude") {
          params.is_noise = 0;
        }
        var is_processed = $('input[name=subject_token_is_processed]:checked').val();
        if (is_processed == "include") {
          params.is_processed = 1;
        } else if (is_processed == "exclude") {
          params.is_processed = 0;
        }
        return params;
      }
    }
  }).on('select2:select', (e) => {
    updateTokenRelationships().then(() => {
      getToken("subject");
    })
  });

  function getToken(target) {
    var promise = $.ajax({
      method: 'GET',
      url: "/admin/token",
      data: {
        "id": $("#" + target + "_token").val()
      }
    });
    return promise.done((data) => {
      console.log(data);
      if (!data.token) {
        return;
      }
      if (target == "subject") {
        if (data.token.type) {
          $('#token_type').val(data.token.type.id).trigger('change');
        } else {
          $('#token_type').val(0).trigger('change');
        }
        $('#is_noise').prop("checked", data.token.is_noise == "1");
      }
      if (data.token.hash) {
        return selectNode(target, data.token.hash).then(() => {
          return zoomIntoNode(data.token.hash);
        });
      }
    });
  }

  $('#update_token_button').on('click', () => {
    var promise = $.ajax({
      method: 'POST',
      url: "/admin/token",
      data: {
        "id": $('#subject_token').val(),
        "is_noise": $('#is_noise').is(':checked') ? 1 : 0,
        "token_type": $('#token_type').val()
      }
    });
    promise.done((data) => {
      console.log(data);
      if ($('#is_noise').is(':checked') == false) {
        updateGraph();
        getToken("subject");
      }
    });
    return false;
  });

  $('#token_type').on("change", (e) => {
    updateTypeAttribute('token_type', graph_schema['labels']);
  });

  function updateTypeAttribute(name, schema) {
    var type = $('#' + name + ' option:selected').text();
    var id_prefix = name + "_attribute_";
    if (type == "None") {
      return;
    }
    $.each($('#' + name + '_attributes > div.dynamic-row'), (k, row) => {
      row = $(row);
      attribute = row.data('attribute');

      if (attribute.type == "date") {
        $('#' + id_prefix + attribute.name).datetimepicker('destroy');
      }
      $(row).remove();
    });
    var attributes = schema[type].filter((v) => { return v['name'] != "name"; });
    $.each(attributes, (k, attribute) => {
      var input_id = id_prefix + attribute.name;
      var row =
        $('<div class="form-row py-1 dynamic-row">' +
          '  <label class="col-sm-2 col-form-label col-form-label-sm text-capitalize" for="' + input_id + '">' + attribute.name + '</label>' +
          '  <div class="col-sm-10">' +
          '    <input type="text" class="form-control form-control-sm" id="' + input_id + '" placeholder="' + attribute.placeholder + '"></input>' +
          '  </div>' +
          '</div>');

      row.data("attribute", attribute);
      $('#' + name + '_attributes').append(row);
      if (attribute.type == "date") {
        console.log($('#' + input_id));
        $('#' + input_id).datetimepicker({
          format: 'Y-m-d',
          timepicker: false
        });
      }
    });
    if(attributes.length > 0){
      $('#' + name + '_attributes_container').css('display', 'flex');
    } else {
      $('#' + name + '_attributes_container').hide();
    }
  }

  $('#remove_token_button').on('click', () => {
    var promise = $.ajax({
      method: 'DELETE',
      url: "/admin/token?id=" + $('#subject_token').val()
    });
    promise.done((data) => {
      console.log(data);
      updateGraph();
    });
    return false;
  });

  $("#object_token").select2({
    placeholder: 'Object Token',
    ajax: {
      url: "/admin/tokens",
      dataType: 'json',
      delay: 250,
      minimumInputLength: 1,
      allowClear: true,

      data: (params) => {
        params.is_noise = 0;
        params.is_processed = 1;
        return params;
      }
    }
  }).on('select2:select', (e) => {
    updateTokenRelationships();
    getToken("object");
  });
  $('#token_relationship_type').change(() => {
    updateTokenRelationships();
  });
  $('#update_token_relationship_button').on('click', () => {
    var promise = $.ajax({
      method: 'POST',
      url: "/admin/token_relationship",
      data: {
        "object_token_id": $('#object_token').val(),
        "subject_token_id": $('#subject_token').val(),
        "token_relationship_type_id": $('#token_relationship_type').val(),
        "token_relationship_from": $('#relationship_from').val(),
        "token_relationship_to": $('#relationship_to').val(),
      }
    });
    promise.done((data) => {
      console.log(data);
      updateGraph();
      updateTokenRelationships();
      setTimeout(() => {
        getToken("subject");
      }, 300);

    });
    return false;
  });

  $('#remove_token_relationship_button').on('click', () => {
    var promise = $.ajax({
      method: 'DELETE',
      url: "/admin/token_relationship?id=" + $('#token_relationship_type').data('relationship_id')
    });
    promise.done((data) => {
      console.log(data);
      updateGraph();
    });
    return false;
  });

  function updateTokenRelationships() {
    var promise = $.ajax({
      method: 'GET',
      url: '/admin/token_relationship',
      data: {
        "object_token_id": $('#object_token').val(),
        "subject_token_id": $('#subject_token').val(),
        "token_relationship_type_id": $('#token_relationship_type').val()
      }
    });
    return promise.done((data) => {
      console.log(data);
      if (data.token_relationship) {
        var rel = data.token_relationship;
        $('#token_relationship_type').data('relationship_id', rel.id);
      } else {
        $('#token_relationship_type').data('relationship_id', null);
      }
      updateTypeAttribute('token_relationship_type', graph_schema['relationships']);
    });
  }

  svg = d3.select("svg");
  var simulation;
  var target_w = 0;
  var target_h = 0;
  var graph = { nodes: [], links: [] }
  var color = d3.scaleOrdinal(d3.schemeCategory10);
  svg.append("defs").selectAll("marker")
    .data(["end"])
    .enter().append("marker")
    .attr("id", String)
    .attr("viewBox", "0 -5 10 10")
    .attr("refX", 36)
    .attr("refY", 0)
    .attr("markerWidth", 4)
    .attr("markerHeight", 4)
    .attr("orient", "auto")
    .append("path")
    .attr("d", "M0,-5L10,0L0,5");
  var layer = svg.append("g")
    .attr("class", "everything");
  layer.append("g")
    .attr("class", "links")
  layer.append("g")
    .attr("class", "nodes")

  function simulation_create(mode = 'initial') {
    target_w = $('#graph').parent().outerWidth();
    target_h = window.innerHeight - $('nav.navbar').outerHeight() - 20;
    svg.attr('width', target_w).attr('height', target_h);
    if (mode == 'initial') {
      simulation = d3.forceSimulation()
        .on("tick", () => {
          svg.selectAll('g.link line')
            .attr("x1", (d) => { return d.source.x; })
            .attr("y1", (d) => { return d.source.y; })
            .attr("x2", (d) => { return d.target.x; })
            .attr("y2", (d) => { return d.target.y; });

          svg.selectAll('g.link text')
            .attr("x", (d) => {
              return (d.source.x + d.target.x) / 2;
            })
            .attr("y", (d) => {
              return (d.source.y + d.target.y) / 2;
            });
          svg.selectAll('g.node').attr("transform", (d) => {
            return "translate(" + d.x + "," + d.y + ")";
          })
        });
      simulation
        .force('link', d3.forceLink().id((d) => { return d.hash; })
          .distance(50)
          .strength(1))
      simulation
        .force('charge', d3.forceManyBody()
          .strength(-50))
      simulation
        .force('center', d3.forceCenter(target_w / 2, target_h / 2))
      simulation
        .force('collide', d3.forceCollide(15));

    } else {
      if (!d3.event.active) simulation.alphaTarget(1).restart();
      simulation.force('center', d3.forceCenter(target_w / 2, target_h / 2));
    }
  }

  d3.select(window).on('resize', () => {
    simulation_create('resize');
  });

  function updateGraph(initial = false) {
    d3.json("/admin/graph").then((data) => {
      if (initial) {
        graph = data;
      } else {
        graph = applyUpdate(graph, data);
      }
      updateGraphWorker(initial)
    });
  }

  function updateGraphWorker(initial = false) {
    link = svg.select('.links').selectAll('g.link').data(graph.links, (d) => { return "link-" + d.id; })
    newLinks = link.enter().insert("g")
    newLinks
      .attr("class", "link")
      .attr('id', (d) => { return "link-" + d.id; })
      .on("click", (d) => {
        selectRelation(d.id, d.type.id, d.source.hash, d.target.hash);
      });
    newLinks.append("line")
      .attr("marker-end", "url(#end)");

    newLinks.append("text")
      .attr("class", "link-label")
      .text((d) => {
        return d.type.display_name;
      })
    link.exit().remove();

    node = svg.select('.nodes').selectAll('g.node').data(graph.nodes)
    newNodes = node.enter().insert("g")
    newNodes
      .attr("class", "node")
      .attr('id', (d) => { return "node-" + d.hash; })
      .call(d3.drag()
        .on("start", dragstarted)
        .on("drag", dragged)
        .on("end", dragended))
      .on("click", (d) => {
        console.log(d);
        if (event.shiftKey) {
          selectObjectNode(d.hash);
        } else {
          selectSubjectNode(d.hash);
        }
        d3.select(".links .selected").classed("selected", false);
      });

    newNodes.append("circle")
      .attr("r", 10)
      .attr("fill", (d) => { return color(d.type.id); });

    newNodes.append("text")
      .attr("class", "node-label")
      .attr("y", 3)
      .text((d) => {
        return d.name;
      });
    newNodes.append("title")
      .text(function (d, i) { return d.hash; });
    node.exit().remove();

    simulation.nodes(graph.nodes)
    simulation.force("link").links(graph.links)
    if (!initial) {
      simulation.alpha(0.2).restart();
    }
  }

  svg.on('click', (e) => {
    $("#subject_token").select2("close");
    $("#object_token").select2("close");
  });

  zoom = d3.zoom()
    .scaleExtent([0.2, 3])
    .on("zoom", zoomed);

  svg.call(zoom);

  layer_transform = { "x": 0, "y": 0, "scale": 1 };
  function zoomed() {
    layer.attr("transform", d3.event.transform);
    layer_transform.x = d3.event.transform.x;
    layer_transform.y = d3.event.transform.y;
    layer_transform.scale = d3.event.transform.k;
  }

  function zoomIntoNode(hash) {
    var element = svg.select('#node-' + hash);
    zoomIntoElement(element);
  }
  function zoomIntoElement(element) {
    var bounds = element.node().getBoundingClientRect();
    var
      x = bounds.x + bounds.width / 2,
      y = bounds.y - bounds.height / 2,
      scale = Math.max(1, Math.min(3, 0.85 / Math.max(bounds.width / target_w, bounds.height / target_h))),
      position_scale = scale / layer_transform.scale;
    translate = [layer_transform.x + target_w / 2 - x * position_scale, layer_transform.y + target_h / 2 - y * position_scale];
    svg.transition()
      .duration(750)
      .call(zoom.transform, d3.zoomIdentity.translate(translate[0], translate[1]).scale(scale));
  }

  $('#resetGraphButton').on('click', (e) => {
    //zoomIntoNode("72d21e62-643e-437e-8420-a3596a8beacd");
    svg.transition()
      .duration(750)
      .call(zoom.transform, d3.zoomIdentity);
    return false;
  });

  function dragstarted(d) {
    if (!d3.event.active) simulation.alphaTarget(0.3).restart();
    d.fx = d.x;
    d.fy = d.y;
  }

  function dragged(d) {
    d.fx = d3.event.x;
    d.fy = d3.event.y;
  }

  function dragended(d) {
    if (!d3.event.active) simulation.alphaTarget(0);
    d.fx = null;
    d.fy = null;
  }

  function selectRelation(id, type_id, source_hash, target_hash) {
    d3.select(".links .selected").classed("selected", false);
    d3.select("#link-" + id).classed("selected", true);
    $('#token_relationship_type').val(type_id)
    selectSubjectNode(source_hash).then(() => {
      return selectObjectNode(target_hash)
    }).then(() => {
      return updateTokenRelationships();
    });
  }

  function selectSubjectNode(hash) {
    return selectNode("subject", hash);
  }
  function selectObjectNode(hash) {
    return selectNode("object", hash);
  }
  function selectNode(type, hash) {
    var className, selectForm;
    if (type == "object") {
      className = "selectedObjectToken";
      selectForm = $('#object_token');
    } else if (type == "subject") {
      className = "selectedSubjectToken";
      selectForm = $('#subject_token');
    } else {
      return;
    }
    d3.select(".nodes ." + className).classed(className, false);
    d3.select("#node-" + hash).classed(className, true);
    var promise = $.ajax({
      method: 'GET',
      url: "/admin/token",
      data: {
        "hash": hash
      }
    });
    return promise.then((data) => {
      console.log(data);
      if (selectForm.find("option[value='" + data.token.id + "']").length) {
        selectForm.val(data.token.id).trigger('change');
      } else {
        var newOption = new Option(data.token.base_form, data.token.id, true, true);
        selectForm.append(newOption).trigger('change');
      }
      if (type == "subject") {
        $('#token_type').val(data.token.type.id).trigger('change');
      }
    });
  }

  function applyUpdate(current, updated) {
    current.nodes = applyUpdateWorker(updated.nodes, current.nodes, "append");
    current.links = applyUpdateWorker(updated.links, current.links, "append");

    current.nodes = applyUpdateWorker(current.nodes, updated.nodes, "remove");
    current.links = applyUpdateWorker(current.links, updated.links, "remove");
    return current;
  }
  function applyUpdateWorker(a, b, action) {
    var diff = [];
    $.each(a, (k1, v1) => {
      var found = true;
      $.each(b, (k2, v2) => {
        if (v1.id == v2.id) {
          found = false;
          return false;
        }
      });
      if (found) {
        if (action == "append") {
          diff.push(v1);
        } else {
          diff.push(k1);
        }
      }
    });
    var target = a;
    if (action == "append") {
      target = b;
    }

    $.each(diff, (k, v) => {
      if (action == "append") {
        target.push(v);
      } else {
        target.splice(v, 1);
      }
    });
    return target;
  }

  simulation_create();
  updateGraph(true);
});