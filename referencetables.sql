CREATE TABLE center_types
(
  id integer NOT NULL DEFAULT nextval('center_types_id_seq'::regclass),
  name character varying,
  lang character varying,
  CONSTRAINT center_types_pkey PRIMARY KEY (id)
);

INSERT INTO center_types (name, lang) VALUES ('Oberzentrum', 'de');
INSERT INTO center_types (name, lang) VALUES ('Mittelzentrum', 'de');
INSERT INTO center_types (name, lang) VALUES ('Mittelzentrum mit Teilfunktionen eines Oberzentrums', 'de');
INSERT INTO center_types (name, lang) VALUES ('Mittelzentrum im Verdichtungsraum', 'de');
INSERT INTO center_types (name, lang) VALUES ('Mittelzentraler Verbund', 'de');
INSERT INTO center_types (name, lang) VALUES ('Kreisangehörige Stadt', 'de');

CREATE TABLE centers_de
(
  city character varying,
  state character varying,
  type integer,
  "group" integer
);

CREATE INDEX centers_de_index ON centers_de USING hash ( city );

COPY centers_de FROM '/Users/carsten/Dropbox/Code/CentralPlaceWiki/centers_de.csv' DELIMITER ',' CSV QUOTE E'\'';
