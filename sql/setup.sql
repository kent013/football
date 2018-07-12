DROP TABLE IF EXISTS current_crawler_jobs;
DROP TABLE IF EXISTS crawler_job_logs;
DROP TABLE IF EXISTS crawler_jobs;
DROP TABLE IF EXISTS article_contents;
DROP TABLE IF EXISTS articles;
DROP TABLE IF EXISTS feeds;
DROP TABLE IF EXISTS site_categories;
DROP TABLE IF EXISTS site_types;

CREATE TABLE site_categories (
  `id` INT NOT NULL AUTO_INCREMENT,
  `display_name` TEXT NOT NULL,
  `created_at` TIMESTAMP NOT NULL DEFAULT current_timestamp,
  `updated_at` TIMESTAMP NOT NULL DEFAULT current_timestamp ON UPDATE current_timestamp,

  PRIMARY KEY (`id`)
);

CREATE TABLE site_types (
  `id` INT NOT NULL AUTO_INCREMENT,
  `display_name` TEXT NOT NULL,
  `created_at` TIMESTAMP NOT NULL DEFAULT current_timestamp,
  `updated_at` TIMESTAMP NOT NULL DEFAULT current_timestamp ON UPDATE current_timestamp,

  PRIMARY KEY (`id`)
);

CREATE TABLE feeds (
  `id` INT NOT NULL AUTO_INCREMENT,
  `title` TEXT NOT NULL,
  `language` VARCHAR(20) NOT NULL,
  `feed_url` VARCHAR(1000) NOT NULL,
  `site_url` VARCHAR(1000) NOT NULL,
  `description` TEXT NULL,
  `site_category_id` INT NOT NULL,
  `site_type_id` INT NOT NULL,
  `scraped_at` TIMESTAMP NULL,
  `created_at` TIMESTAMP NOT NULL DEFAULT current_timestamp,
  `updated_at` TIMESTAMP NOT NULL DEFAULT current_timestamp ON UPDATE current_timestamp,

  PRIMARY KEY (`id`),
  INDEX `feeds_language_idx` (`language` ASC),
  INDEX `feeds_site_category_id_idx` (`site_category_id` ASC),
  CONSTRAINT `feeds_site_category_id`
    FOREIGN KEY (`site_category_id`)
    REFERENCES `football`.`site_categories` (`id`),
  INDEX `feeds_site_type_id_idx` (`site_type_id` ASC),
  CONSTRAINT `feeds_site_type_id`
    FOREIGN KEY (`site_type_id`)
    REFERENCES `football`.`site_types` (`id`)
);

CREATE TABLE articles (
  `id` INT NOT NULL AUTO_INCREMENT,
  `title` VARCHAR(1000) NOT NULL,
  `summary` TEXT NOT NULL,
  `creator` VARCHAR(255) NOT NULL,
  `url` VARCHAR(1000) NOT NULL,
  `hash` VARCHAR(255) NOT NULL,
  `subject` VARCHAR(255) NOT NULL,
  `feed_id` INT NOT NULL,
  `published_at` TIMESTAMP NULL,
  `scraped_at` TIMESTAMP NULL,
  `created_at` TIMESTAMP NOT NULL DEFAULT current_timestamp,
  `updated_at` TIMESTAMP NOT NULL DEFAULT current_timestamp ON UPDATE current_timestamp,

  PRIMARY KEY (`id`),
  INDEX `articles_published_at_idx` (`published_at` ASC),
  INDEX `articles_hash_idx` (`hash` ASC),
  INDEX `articles_feed_id_idx` (`feed_id` ASC),
  CONSTRAINT `articles_feed_id`
    FOREIGN KEY (`feed_id`)
    REFERENCES `football`.`feeds` (`id`)
);

CREATE TABLE article_contents (
  `id` INT NOT NULL AUTO_INCREMENT,
  `content` MEDIUMTEXT NOT NULL,
  `extracted_content` MEDIUMTEXT NULL,
  `primary_image_url` VARCHAR(1000) NULL,
  `article_hash` VARCHAR(255) NOT NULL,
  `content_hash` VARCHAR(255) NOT NULL,
  `similar_article_calculated` BOOLEAN NOT NULL DEFAULT 0,
  `tweeted` BOOLEAN NOT NULL DEFAULT 0,
  `created_at` TIMESTAMP NOT NULL DEFAULT current_timestamp,
  `updated_at` TIMESTAMP NOT NULL DEFAULT current_timestamp ON UPDATE current_timestamp,

  PRIMARY KEY (`id`),
  INDEX `article_contents_article_hash_idx` (`article_hash` ASC),
  INDEX `article_contents_extracted_contents_idx` (`extracted_content`(1) ASC)
);

CREATE TABLE similar_articles (
  `id` INT NOT NULL AUTO_INCREMENT,
  `article_hash` VARCHAR(255) NOT NULL,
  `similar_article_hash` VARCHAR(255) NOT NULL,
  `score` FLOAT NOT NULL,
  `created_at` TIMESTAMP NOT NULL DEFAULT current_timestamp,
  `updated_at` TIMESTAMP NOT NULL DEFAULT current_timestamp ON UPDATE current_timestamp,

  PRIMARY KEY (`id`),
  INDEX `article_contents_article_hash_idx` (`article_hash` ASC),
  INDEX `article_contents_similar_article_hash_idx` (`similar_article_hash` ASC)
);

CREATE TABLE crawler_jobs (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `feed_id` int(11) DEFAULT NULL,
  `type` varchar(255) DEFAULT NULL,
  `target` varchar(255) DEFAULT NULL,
  `instruction` varchar(255) DEFAULT NULL,
  `priority` int(11) DEFAULT NULL,
  `error_message` text,
  `failed_at` DATETIME DEFAULT NULL,
  `completed_at` DATETIME DEFAULT NULL,
  `created_at` DATETIME DEFAULT NULL,
  `updated_at` DATETIME DEFAULT NULL,
  `started_at` DATETIME DEFAULT NULL,
  `additional_information` TEXT,
  `retry_at` DATETIME DEFAULT NULL,
  `retry_count` int(11) DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `index_crawler_jobs_on_feed_id` (`feed_id`) USING BTREE,
  KEY `index_crawler_jobs_on_created_at` (`created_at`),
  KEY `index_crawler_jobs_on_type_failed_at_completed_at` (`type`,`failed_at`,`completed_at`),
  KEY `index_crawler_jobs_on_type_started_at_feed_id` (`type`,`started_at`,`feed_id`),
  KEY `index_crawler_jobs_on_type_started_at` (`type`,`started_at`),
  KEY `index_crawler_jobs_on_type` (`type`),
  KEY `index_crawler_jobs_on_target` (`target`),
  KEY `index_crawler_jobs_on_completed_at` (`completed_at`),
  KEY `index_crawler_jobs_on_failed_at` (`failed_at`),
  KEY `index_crawler_jobs_on_retry_at` (`retry_at`),
  KEY `index_crawler_jobs_on_id_started_at` (`id`,`started_at`),
  KEY `index_crawler_jobs_on_started_at` (`started_at`),
  KEY `index_crawler_jobs_on_priority` (`priority`),
  KEY `index_crawler_jobs_for_search` (`started_at`,`feed_id`,`retry_at`,`priority`),
  CONSTRAINT `fk_rails_f6323d576c` FOREIGN KEY (`feed_id`) REFERENCES `feeds` (`id`)
);

CREATE TABLE crawler_job_logs (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `crawler_job_id` int(11) DEFAULT NULL,
  `feed_id` int(11) DEFAULT NULL,
  `type` varchar(255) DEFAULT NULL,
  `target` varchar(255) DEFAULT NULL,
  `instruction` varchar(255) DEFAULT NULL,
  `priority` int(11) DEFAULT NULL,
  `error_message` text,
  `failed_at` datetime DEFAULT NULL,
  `completed_at` datetime DEFAULT NULL,
  `job_created_at` datetime DEFAULT NULL,
  `job_updated_at` datetime NOT NULL,
  `created_at` datetime NOT NULL,
  `started_at` datetime DEFAULT NULL,
  `additional_information` text,
  `retry_at` datetime DEFAULT NULL,
  `retry_count` int(11) DEFAULT '0',
  PRIMARY KEY (`id`)
);

CREATE TABLE `current_crawler_jobs` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `feed_id` int(11) DEFAULT NULL,
  `type` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `index_current_unique_current_crawler_jobs` (`feed_id`,`type`)
);

INSERT INTO site_categories(id, display_name) VALUES (1, 'サッカー');
INSERT INTO site_types(id, display_name) VALUES (1, '公式サイト');
INSERT INTO site_types(id, display_name) VALUES (2, 'ニュースサイト');
INSERT INTO site_types(id, display_name) VALUES (3, 'まとめサイト');
INSERT INTO site_types(id, display_name) VALUES (4, 'Blog');

INSERT INTO feeds(id, site_category_id, site_type_id, language, title, site_url, feed_url, description) VALUES(1, 1, 3, 'ja', 'SAMURAI Footballers', 'http://samuraisoccer.doorblog.jp/', 'http://samuraisoccer.doorblog.jp/index.rdf', '～海外への挑戦～');
INSERT INTO feeds(id, site_category_id, site_type_id, language, title, site_url, feed_url, description) VALUES(2, 1, 3, 'ja', 'Samurai GOAL', 'http://samuraigoal.doorblog.jp/', 'http://samuraigoal.doorblog.jp/index.rdf', '');
INSERT INTO feeds(id, site_category_id, site_type_id, language, title, site_url, feed_url, description) VALUES(3, 1, 3, 'ja', 'フットカルチョ', 'http://blog.livedoor.jp/footcalcio/', 'http://blog.livedoor.jp/footcalcio/index.rdf', '');
INSERT INTO feeds(id, site_category_id, site_type_id, language, title, site_url, feed_url, description) VALUES(4, 1, 3, 'ja', 'WorldFootballNewS', 'http://worldfn.net/', 'http://worldfn.net/index.rdf', '世界のサッカーニュースに対する管理人Ａ　ｔｏ　Ｚ　のつぶやきをまとめる');
INSERT INTO feeds(id, site_category_id, site_type_id, language, title, site_url, feed_url, description) VALUES(5, 1, 3, 'ja', 'サッカーミックスジュース', 'http://blog.livedoor.jp/soccerkusoyarou/', 'http://blog.livedoor.jp/soccerkusoyarou/index.rdf', '2ちゃんねるサッカー関連スレのコピペブログです。主に短レス系を取り扱っています。');
INSERT INTO feeds(id, site_category_id, site_type_id, language, title, site_url, feed_url, description) VALUES(6, 1, 3, 'ja', 'NO FOOTY NO LIFE', 'http://nofootynolife.blog.fc2.com/', 'http://nofootynolife.blog.fc2.com/?xml', '');
INSERT INTO feeds(id, site_category_id, site_type_id, language, title, site_url, feed_url, description) VALUES(7, 1, 3, 'ja', 'カルチョまとめブログ', 'http://www.calciomatome.net/', 'http://www.calciomatome.net/index20.rdf', '国内サッカー、日本代表、海外サッカー問わずサッカー関係記事のまとめブログです。');
INSERT INTO feeds(id, site_category_id, site_type_id, language, title, site_url, feed_url, description) VALUES(8, 1, 3, 'ja', 'フットボール速報', 'http://football-2ch.com/', 'http://football-2ch.com/index.rdf', '２ちゃんねるのサッカー情報を簡単に(下手クソ)にまとめています。');
INSERT INTO feeds(id, site_category_id, site_type_id, language, title, site_url, feed_url, description) VALUES(9, 1, 3, 'ja', 'ドメサカブログ', 'http://blog.domesoccer.jp', 'http://blog.domesoccer.jp/feed', 'このブログでは国内サッカー(domestic soccer)関連の情報を紹介しています。 Jリーグ関連がメインですが、代表や海外ネタを扱うこともあります。');
INSERT INTO feeds(id, site_category_id, site_type_id, language, title, site_url, feed_url, description) VALUES(10, 1, 3, 'ja', 'footballnet【サッカーまとめ】', 'http://footballnet.2chblog.jp/', 'http://footballnet.2chblog.jp/index.rdf', 'footballnet【サッカーまとめ】');
INSERT INTO feeds(id, site_category_id, site_type_id, language, title, site_url, feed_url, description) VALUES(11, 1, 4, 'ja', 'Blog版 蹴閑ガゼッタ', 'http://gazfootball.com/blog/', 'http://gazfootball.com/blog/feed/', '日本代表・海外リーグ・たまにJリーグを網羅する節操なしサッカーコラムマガジン');
INSERT INTO feeds(id, site_category_id, site_type_id, language, title, site_url, feed_url, description) VALUES(12, 1, 2, 'ja', 'ゲキサカ', 'https://web.gekisaka.jp/', 'https://web.gekisaka.jp/feed', 'ゲキサカ。講談社が運営するサッカー総合サイト。Jリーグ、日本代表、海外サッカーから高校サッカー、大学サッカーまであらゆるジャンルの最新ニュースを速報で掲載。膨大なボリュームの写真ニュースのほか、コラム、試合速報、選手名鑑などのデータも充実。');
INSERT INTO feeds(id, site_category_id, site_type_id, language, title, site_url, feed_url, description) VALUES(13, 1, 2, 'ja', 'フットボールチャンネル', 'https://www.footballchannel.jp', 'https://www.footballchannel.jp/feed/', '『フットボール批評』と『フットボールサミット』の編集部が制作するWEBサイト。圧倒的な論説をお届けします。');
INSERT INTO feeds(id, site_category_id, site_type_id, language, title, site_url, feed_url, description) VALUES(14, 1, 2, 'ja', '海外サッカー - Number Web', 'http://number.bunshun.jp/subcategory/%E6%B5%B7%E5%A4%96%E3%82%B5%E3%83%83%E3%82%AB%E3%83%BC/column', 'http://number.bunshun.jp/list/rsssports?w=%E6%B5%B7%E5%A4%96%E3%82%B5%E3%83%83%E3%82%AB%E3%83%BC', 'Number Web の海外サッカー新着コラムを掲載しています。');
INSERT INTO feeds(id, site_category_id, site_type_id, language, title, site_url, feed_url, description) VALUES(15, 1, 2, 'ja', 'サッカー日本代表 - Number Web', 'http://number.bunshun.jp/subcategory/%E3%82%B5%E3%83%83%E3%82%AB%E3%83%BC%E6%97%A5%E6%9C%AC%E4%BB%A3%E8%A1%A8/column', 'http://number.bunshun.jp/list/rsssports?w=%E3%82%B5%E3%83%83%E3%82%AB%E3%83%BC%E6%97%A5%E6%9C%AC%E4%BB%A3%E8%A1%A8', 'Number Web のサッカー日本代表新着コラムを掲載しています。');
INSERT INTO feeds(id, site_category_id, site_type_id, language, title, site_url, feed_url, description) VALUES(16, 1, 2, 'ja', 'Jリーグ - Number Web', 'http://number.bunshun.jp/subcategory/J%E3%83%AA%E3%83%BC%E3%82%B0/column', 'http://number.bunshun.jp/list/rsssports?w=J%E3%83%AA%E3%83%BC%E3%82%B0', 'Number Web のJリーグ新着コラムを掲載しています。');
INSERT INTO feeds(id, site_category_id, site_type_id, language, title, site_url, feed_url, description) VALUES(17, 1, 2, 'ja', 'サッカー - nikkansports.com', 'http://www.nikkansports.com/soccer/index.html', 'https://www.nikkansports.com/soccer/atom.xml', 'ニッカンスポーツ・コム サッカー最新ニュース');
INSERT INTO feeds(id, site_category_id, site_type_id, language, title, site_url, feed_url, description) VALUES(18, 1, 2, 'ja', '「サッカー」の最新ニュース - SANSPO.COM（サンスポ・コム）', 'http://www.sanspo.com/soccer/soccer.html', 'http://www.sanspo.com/rss/soccer/news/soccer-n.xml', 'SANSPO.COM（サンスポ・コム）に掲載されている「サッカー」の最新ニュースを提供しています。');
INSERT INTO feeds(id, site_category_id, site_type_id, language, title, site_url, feed_url, description) VALUES(19, 1, 2, 'ja', 'サッカーダイジェストWeb', 'http://www.soccerdigestweb.com/', 'http://www.soccerdigestweb.com/RSS.rdf', 'サッカーダイジェストWebの更新情報');
INSERT INTO feeds(id, site_category_id, site_type_id, language, title, site_url, feed_url, description) VALUES(20, 1, 1, 'ja', 'BLOGOLA', 'http://blogola.jp', 'http://blogola.jp/feed', 'サッカー専門新聞ELGOLAZO web版');
INSERT INTO feeds(id, site_category_id, site_type_id, language, title, site_url, feed_url, description) VALUES(21, 1, 2, 'ja', 'JFA｜公益財団法人日本サッカー協会', 'http://www.jfa.jp', 'https://www.jfa.jp/feed.rss', 'JFA｜公益財団法人日本サッカー協会 ');
INSERT INTO feeds(id, site_category_id, site_type_id, language, title, site_url, feed_url, description) VALUES(22, 1, 2, 'ja', 'Goal.com', 'http://goal.com', 'http://news.livedoor.com/category/vender/goal/', 'Goal.com');
INSERT INTO feeds(id, site_category_id, site_type_id, language, title, site_url, feed_url, description) VALUES(23, 1, 1, 'en', 'FIFA.com - Latest News', 'http://www.fifa.com/index.html', 'http://www.fifa.com/rss/index.xml', 'Breaking football news from around the world from FIFA.com. Tags: football news, soccer news, world cup, fifa world cup, fifa, soccer, football, sport');
INSERT INTO feeds(id, site_category_id, site_type_id, language, title, site_url, feed_url, description) VALUES(24, 1, 2, 'en', 'BBC Sport - Football', 'http://www.bbc.co.uk/sport/', 'http://feeds.bbci.co.uk/sport/football/rss.xml?edition=int', 'BBC Sport - Football');
INSERT INTO feeds(id, site_category_id, site_type_id, language, title, site_url, feed_url, description) VALUES(25, 1, 2, 'en', 'ESPN FC News', 'http://global.espn.com/football/?src=com', 'http://www.espnfc.com/rss', 'ESPN FC News RSS Feed');
INSERT INTO feeds(id, site_category_id, site_type_id, language, title, site_url, feed_url, description) VALUES(26, 1, 3, 'ja', 'サカサカ10【サッカーまとめ速報', 'http://sakasaka10.blog.jp/', 'http://sakasaka10.blog.jp/atom.xml', '海外・国内のサッカー情報まとめ');
INSERT INTO feeds(id, site_category_id, site_type_id, language, title, site_url, feed_url, description) VALUES(27, 1, 3, 'ja', 'ワールドサッカーファン　海外の反応', 'http://blog.livedoor.jp/kaigainoomaera-worldsoccer/', 'http://blog.livedoor.jp/kaigainoomaera-worldsoccer/index.rdf', '');
INSERT INTO feeds(id, site_category_id, site_type_id, language, title, site_url, feed_url, description) VALUES(28, 1, 3, 'ja', 'サッカーレボリューション', 'http://blog.livedoor.jp/soccerrevolution/', 'http://blog.livedoor.jp/soccerrevolution/index.rdf', 'サポーターの真実の声を伝えたい。海外日本人、日本代表、Jリーグをピックアップ！');
INSERT INTO feeds(id, site_category_id, site_type_id, language, title, site_url, feed_url, description) VALUES(29, 1, 4, 'ja', 'JとFの歩き方', 'http://jf-2016.com/', 'http://jf-2016.com/atom.xml', 'ブログのテーマは「自国リーグを育てる」。JリーグとFリーグ関連のニュースを管理人の主観でまとめます。');
INSERT INTO feeds(id, site_category_id, site_type_id, language, title, site_url, feed_url, description) VALUES(30, 1, 3, 'ja', '海外サッカーチャンネル', 'http://world-soccer.2chblog.jp/', 'http://world-soccer.2chblog.jp/atom.xml', '');
INSERT INTO feeds(id, site_category_id, site_type_id, language, title, site_url, feed_url, description) VALUES(31, 1, 3, 'ja', 'Ｊ２いろいろ', 'http://j2iroiro.blog.jp/', 'http://j2iroiro.blog.jp/index.rdf', '～サッカーＪ２を中心にまとめます～');
INSERT INTO feeds(id, site_category_id, site_type_id, language, title, site_url, feed_url, description) VALUES(32, 1, 3, 'ja', 'footballlog', 'http://footballlog.blog.jp/', 'http://footballlog.blog.jp/atom.xml', '2chまとめ');
INSERT INTO feeds(id, site_category_id, site_type_id, language, title, site_url, feed_url, description) VALUES(33, 1, 3, 'ja', 'サカバナブログ', 'http://sakabana.blog.jp/', 'http://sakabana.blog.jp/index.rdf', 'サカバナブログ');
INSERT INTO feeds(id, site_category_id, site_type_id, language, title, site_url, feed_url, description) VALUES(34, 1, 3, 'ja', 'サッカー情報～僕は自分が見たなにがししか信じない～', 'http://blog.livedoor.jp/keydrop/', 'http://blog.livedoor.jp/keydrop/atom.xml', 'サッカー情報～僕は自分が見たなにがししか信じない～');
INSERT INTO feeds(id, site_category_id, site_type_id, language, title, site_url, feed_url, description) VALUES(35, 1, 3, 'ja', '吹田のサポがまとめます。', 'http://suitasapo.doorblog.jp', 'http://suitasapo.doorblog.jp/atom.xml', '吹田のサポがまとめます。');
INSERT INTO feeds(id, site_category_id, site_type_id, language, title, site_url, feed_url, description) VALUES(36, 1, 3, 'ja', 'スパねこ　～スパイクを履いたねこ～', 'http://supaneco.com/', 'http://supaneco.com/index.rdf', '海外でプレーしている日本人サッカー選手の情報を取り上げるサイトです。ニュース、試合に対する独自の視点で管理人がコメントをしています。また、独自の記事も配信します。コメント欄でディベートを楽しみましょう。');
INSERT INTO feeds(id, site_category_id, site_type_id, language, title, site_url, feed_url, description) VALUES(37, 1, 3, 'ja', 'コミュサカまとめブログ', 'http://blog.livedoor.jp/commusoccer/', 'http://blog.livedoor.jp/commusoccer/index.rdf', '主にサッカーのJ3、JFL、地域リーグ、都道府県リーグを見ながら、フットサル、障害者サッカーの情報も取り扱っています。');
INSERT INTO feeds(id, site_category_id, site_type_id, language, title, site_url, feed_url, description) VALUES(38, 1, 3, 'ja', 'フットボールちゃんねる', 'http://footballchan.blog.jp/', 'http://footballchan.blog.jp/atom.xml', 'サッカー　２ちゃんねるまとめ');
INSERT INTO feeds(id, site_category_id, site_type_id, language, title, site_url, feed_url, description) VALUES(39, 1, 3, 'ja', 'Foot Ball Styleヾ(*・∀・)/ (サッカー速報まとめ)', 'http://soccer-matomedayo.blog.jp/', 'http://soccer-matomedayo.blog.jp/atom.xml', '2ch（２ちゃんねる）の海外・欧州サッカーや日本代表等のサッカーに関する記事をまとめています(*‘ω‘ *) Foot Ball Style(サッカー速報まとめ) また管理人によるリーグ戦やCLの順位予想なども行っています！');
INSERT INTO feeds(id, site_category_id, site_type_id, language, title, site_url, feed_url, description) VALUES(40, 1, 3, 'ja', 'J２まとめブログ', 'http://j2matome.doorblog.jp/', 'http://j2matome.doorblog.jp/index.rdf', '');
INSERT INTO feeds(id, site_category_id, site_type_id, language, title, site_url, feed_url, description) VALUES(41, 1, 3, 'ja', 'サッカーニュース速報', 'http://blog.livedoor.jp/football_news001/', 'http://blog.livedoor.jp/football_news001/index.rdf', '主に2chサッカー記事まとめをお届け');
INSERT INTO feeds(id, site_category_id, site_type_id, language, title, site_url, feed_url, description) VALUES(42, 1, 3, 'ja', 'サッカーまとめチャンネルG', 'http://soccer-goal.2chblog.jp/', 'http://soccer-goal.2chblog.jp/index.rdf', '国内・海外の最新サッカーニュースまとめ');
INSERT INTO feeds(id, site_category_id, site_type_id, language, title, site_url, feed_url, description) VALUES(43, 1, 3, 'ja', '欧州サッカー速報', 'http://euro-foot.ldblog.jp/', 'http://euro-foot.ldblog.jp/atom.xml', '日本代表選手を中心に欧州サッカーの情報をまとめています');
INSERT INTO feeds(id, site_category_id, site_type_id, language, title, site_url, feed_url, description) VALUES(44, 1, 3, 'ja', 'パルセイロ速報', 'http://parceiro.blog.jp/', 'http://parceiro.blog.jp/atom.xml', '長野パルセイロのまとめサイト');
INSERT INTO feeds(id, site_category_id, site_type_id, language, title, site_url, feed_url, description) VALUES(45, 1, 3, 'ja', 'サッカーマニア', 'http://soccermaniajr.ldblog.jp/', 'http://soccermaniajr.ldblog.jp/index.rdf', '');
INSERT INTO feeds(id, site_category_id, site_type_id, language, title, site_url, feed_url, description) VALUES(46, 1, 3, 'ja', 'フットコミュ！', 'http://blog.livedoor.jp/footcomu/', 'http://blog.livedoor.jp/footcomu/atom.xml', '');
INSERT INTO feeds(id, site_category_id, site_type_id, language, title, site_url, feed_url, description) VALUES(47, 1, 3, 'ja', 'サカ速＋', 'http://sakasoku.2chblog.jp/', 'http://sakasoku.2chblog.jp/atom.xml', 'サッカーまとめブログです。2ちゃんねる(2ch) のサッカー関連のニュースやネタを取り扱っています。');
INSERT INTO feeds(id, site_category_id, site_type_id, language, title, site_url, feed_url, description) VALUES(48, 1, 3, 'ja', '蹴速～しゅうそく～【サッカーまとめ】', 'http://syusoku-matome.doorblog.jp/', 'http://syusoku-matome.doorblog.jp/atom.xml', '世界のサッカーニュース速報＆まとめ');
INSERT INTO feeds(id, site_category_id, site_type_id, language, title, site_url, feed_url, description) VALUES(49, 1, 3, 'ja', 'サッカー/フットボールニュース', 'http://footballnews.blog.jp/', 'http://footballnews.blog.jp/atom.xml', '国内／国外のサッカーの話題をまとめるサイトです');
INSERT INTO feeds(id, site_category_id, site_type_id, language, title, site_url, feed_url, description) VALUES(50, 1, 3, 'ja', '画像とデータで見るワールドサッカー', 'http://blog.livedoor.jp/footballarashi/', 'http://blog.livedoor.jp/footballarashi/index.rdf', '');
INSERT INTO feeds(id, site_category_id, site_type_id, language, title, site_url, feed_url, description) VALUES(51, 1, 3, 'ja', '進撃の日本代表速報', 'http://shingekinonihondaihyou.blog.jp/', 'http://shingekinonihondaihyou.blog.jp/index.rdf', 'サッカーや野球や主にスポーツなどの日本代表の活躍をみてホルホルしたい方に送る感じです');
INSERT INTO feeds(id, site_category_id, site_type_id, language, title, site_url, feed_url, description) VALUES(52, 1, 3, 'ja', 'Golden Age Football News＋α', 'http://goldenagefootballnews.com/', 'http://goldenagefootballnews.com/index.rdf', '');
INSERT INTO feeds(id, site_category_id, site_type_id, language, title, site_url, feed_url, description) VALUES(53, 1, 3, 'ja', 'サッカーじゃ〜なる　(まとめ)', 'http://blog.livedoor.jp/ronaronap/', 'http://blog.livedoor.jp/ronaronap/atom.xml', '');
INSERT INTO feeds(id, site_category_id, site_type_id, language, title, site_url, feed_url, description) VALUES(54, 1, 3, 'ja', 'SAMURAIサッカーまとめでござる', 'http://samuraicsoccer.blog.jp/', 'http://samuraicsoccer.blog.jp/atom.xml', 'サッカー情報2ch関連のまとめのまとめです。');
INSERT INTO feeds(id, site_category_id, site_type_id, language, title, site_url, feed_url, description) VALUES(55, 1, 3, 'ja', 'サッカーコピペまとめブログ', 'http://soccercopype.ldblog.jp/', 'http://soccercopype.ldblog.jp/atom.xml', '秀逸なコピペ・短レスを紹介していきます。');
INSERT INTO feeds(id, site_category_id, site_type_id, language, title, site_url, feed_url, description) VALUES(56, 1, 3, 'ja', 'サッカーまとめ', 'http://soccermatome.publog.jp/', 'http://soccermatome.publog.jp/index.rdf', '');
INSERT INTO feeds(id, site_category_id, site_type_id, language, title, site_url, feed_url, description) VALUES(57, 1, 3, 'ja', '蹴ステ', 'http://blog.livedoor.jp/footballfannews/', 'http://blog.livedoor.jp/footballfannews/atom.xml', '');
INSERT INTO feeds(id, site_category_id, site_type_id, language, title, site_url, feed_url, description) VALUES(58, 1, 3, 'ja', 'ウッシーちゃんねる【内田篤人＆日本代表関連まとめ】', 'http://blog.livedoor.jp/ftbfun-usshi/', 'http://blog.livedoor.jp/ftbfun-usshi/atom.xml', '内田篤人選手を中心に日本代表関連のまとめ記事サイト');
INSERT INTO feeds(id, site_category_id, site_type_id, language, title, site_url, feed_url, description) VALUES(59, 1, 3, 'ja', '２度ある事は３度ある【サッカーまとめ】', 'http://2doaru3doaru.doorblog.jp/', 'http://2doaru3doaru.doorblog.jp/atom.xml', 'サッカーまとめ');
INSERT INTO feeds(id, site_category_id, site_type_id, language, title, site_url, feed_url, description) VALUES(60, 1, 3, 'ja', '代表どうなった速報', 'http://daihyo.blog.jp/', 'http://daihyo.blog.jp/index.rdf', 'サッカー日本代表に関する暇つぶし話題を集めていきます');
INSERT INTO feeds(id, site_category_id, site_type_id, language, title, site_url, feed_url, description) VALUES(61, 1, 3, 'ja', '女子大生が書く！スポーツまとめ（主にサッカー）', 'http://soccer-football.doorblog.jp/', 'http://soccer-football.doorblog.jp/atom.xml', '2013年6月25日から開始！！始めたばかりですが、今後ともよろしくお願いします！サッカーを中心に色々なスポーツその他面白い記事について取り上げていきたいと思います。');
INSERT INTO feeds(id, site_category_id, site_type_id, language, title, site_url, feed_url, description) VALUES(62, 1, 3, 'ja', 'ジャパフットナカタ', 'http://japanfootball.blog.jp/', 'http://japanfootball.blog.jp/atom.xml', '');
INSERT INTO feeds(id, site_category_id, site_type_id, language, title, site_url, feed_url, description) VALUES(63, 1, 3, 'ja', 'にわかファン！！', 'http://ikemenwcup.blog.jp/', 'http://ikemenwcup.blog.jp/atom.xml', 'サッカー選手の画像とか紹介。イケメン選手まとめコーナーもあるよ！');
INSERT INTO feeds(id, site_category_id, site_type_id, language, title, site_url, feed_url, description) VALUES(64, 1, 3, 'ja', 'FOCI フットボールセンター', 'http://foci-footballcenter.blog.jp/', 'http://foci-footballcenter.blog.jp/atom.xml', '');
INSERT INTO feeds(id, site_category_id, site_type_id, language, title, site_url, feed_url, description) VALUES(65, 1, 3, 'ja', 'サッカーの2chまとめです｜一緒にサッカーを盛り上げて行きましょう!!', 'http://soccer2ch.ldblog.jp/', 'http://soccer2ch.ldblog.jp/index.rdf', 'サッカーについて、2ch・ツイッター・ヤフーニュースからいろいろと話題になっているものを集めました。サッカーファンの皆様一緒に盛り上げて行きましょう!!');
INSERT INTO feeds(id, site_category_id, site_type_id, language, title, site_url, feed_url, description) VALUES(66, 1, 3, 'ja', 'サン速！＠サンフレッチェ広島地元ニュースまとめ', 'http://sansoku.blog.jp/', 'http://sansoku.blog.jp/index.rdf', '広島のサンフレッチェ情報を配信！');
INSERT INTO feeds(id, site_category_id, site_type_id, language, title, site_url, feed_url, description) VALUES(67, 1, 3, 'ja', 'zakzak', 'https://www.zakzak.co.jp/', 'http://rss.rssad.jp/rss/zakzak/soccer.xml', 'zakzakに掲載されているサッカーニュースの見出しを提供しています。');
INSERT INTO feeds(id, site_category_id, site_type_id, language, title, site_url, feed_url, description) VALUES(68, 1, 3, 'ja', 'J SPORTS｜コラム（後藤健生コラム）', 'https://www.jsports.co.jp', 'https://www.jsports.co.jp/press/column/title/4/rss2.xml', 'スポーツ専門放送局J SPORTSがお送りするコラム。');
INSERT INTO feeds(id, site_category_id, site_type_id, language, title, site_url, feed_url, description) VALUES(69, 1, 3, 'ja', 'J SPORTS｜コラム（元川悦子コラム）', 'https://www.jsports.co.jp', 'https://www.jsports.co.jp/press/column/title/3/rss2.xml', 'スポーツ専門放送局J SPORTSがお送りするコラム。');
INSERT INTO feeds(id, site_category_id, site_type_id, language, title, site_url, feed_url, description) VALUES(70, 1, 3, 'ja', 'J SPORTS｜コラム（プレミアリーグコラム）', 'https://www.jsports.co.jp', 'https://www.jsports.co.jp/press/column/title/1/rss2.xml', 'スポーツ専門放送局J SPORTSがお送りするコラム。');
INSERT INTO feeds(id, site_category_id, site_type_id, language, title, site_url, feed_url, description) VALUES(71, 1, 3, 'ja', 'J SPORTS｜コラム（粕谷秀樹のOWN GOAL，FINE GOAL）', 'https://www.jsports.co.jp', 'https://www.jsports.co.jp/press/column/title/60/rss2.xml', 'スポーツ専門放送局J SPORTSがお送りするコラム。');
INSERT INTO feeds(id, site_category_id, site_type_id, language, title, site_url, feed_url, description) VALUES(72, 1, 3, 'ja', 'J SPORTS｜コラム（今週のプレミアムゴール）', 'https://www.jsports.co.jp', 'https://www.jsports.co.jp/press/column/title/64/rss2.xml', 'スポーツ専門放送局J SPORTSがお送りするコラム。');
INSERT INTO feeds(id, site_category_id, site_type_id, language, title, site_url, feed_url, description) VALUES(73, 1, 3, 'ja', 'J SPORTS｜コラム（海外サッカーコラム）', 'https://www.jsports.co.jp', 'https://www.jsports.co.jp/press/column/title/69/rss2.xml', 'スポーツ専門放送局J SPORTSがお送りするコラム。');
INSERT INTO feeds(id, site_category_id, site_type_id, language, title, site_url, feed_url, description) VALUES(74, 1, 3, 'ja', 'J SPORTS｜コラム（土屋雅史コラム）', 'https://www.jsports.co.jp', 'https://www.jsports.co.jp/press/column/title/71/rss2.xml', 'スポーツ専門放送局J SPORTSがお送りするコラム。');
INSERT INTO feeds(id, site_category_id, site_type_id, language, title, site_url, feed_url, description) VALUES(75, 1, 3, 'ja', 'Foot！WEB', 'http://www.jsports.co.jp/tv/foot/', 'https://www.jsports.co.jp/foot/index.xml', 'J SPORTSで放送中のワールドサッカーニュース番組「Foot！」のサイト');
INSERT INTO feeds(id, site_category_id, site_type_id, language, title, site_url, feed_url, description) VALUES(76, 1, 3, 'ja', 'mas o menos', 'https://www.jsports.co.jp/football/jleague/blog/', 'https://www.jsports.co.jp/football/jleague/blog/atom.xml', 'スポーツ専門放送局 J SPORTS 公式ブログ【mas o menos 】');
INSERT INTO feeds(id, site_category_id, site_type_id, language, title, site_url, feed_url, description) VALUES(77, 1, 3, 'ja', 'Qoly', 'https://qoly.jp', 'https://qoly.jp/feed/rss.xml', 'サッカー、日本代表のニュース、移籍情報、ちょっといい話からサッカーゲーム、ユニフォーム、ファッションまで網羅するウェブマガジン');
INSERT INTO feeds(id, site_category_id, site_type_id, language, title, site_url, feed_url, description) VALUES(78, 1, 3, 'ja', 'Football FOX SPORTS', 'https://www.foxsports.com.au/football', 'https://www.foxsports.com.au/content-feeds/football/', 'Latest sports news from Football FOX SPORTS');
INSERT INTO feeds(id, site_category_id, site_type_id, language, title, site_url, feed_url, description) VALUES(79, 1, 3, 'ja', 'つれさか　-徒然サッカー雑記-', 'http://blog.livedoor.jp/aushio/', 'http://blog.livedoor.jp/aushio/atom.xml', '');
INSERT INTO feeds(id, site_category_id, site_type_id, language, title, site_url, feed_url, description) VALUES(80, 1, 3, 'ja', 'トピック「サッカー」のまとめ更新情報', 'https://matome.naver.jp/topic/1Hine', 'https://matome.naver.jp/feed/topic/1Hine', '');
