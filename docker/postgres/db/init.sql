CREATE TABLE VERSIONS (
          id int primary key,
          hw_type varchar(32),
          description varchar(120)
);

CREATE TABLE CLIENTS (
          id int primary key,
          name varchar(64) UNIQUE,
          description varchar(120)
);

CREATE TABLE GROUPS (
          id int primary key,
          description varchar(120),
          client_id int references CLIENTS(id),
          quantity int
);

CREATE TABLE DEVICES (
          id int primary key,
          UDID varchar(64) UNIQUE,
          MAC varchar(32) UNIQUE,
          longitude varchar(12) UNIQUE,
          latitude varchar(12) UNIQUE,
          version_id int references VERSIONS(id),
          group_id int references GROUPS(id)
);
