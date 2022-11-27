CREATE TABLE VERSIONS (
          hw_type varchar(12) primary key,
          description varchar(12)
);

CREATE TABLE CLIENTS (
          id int primary key,
          name varchar(12) UNIQUE,
          description varchar(12)
);

CREATE TABLE GROUPS (
          id int primary key,
          description varchar(12),
          client_id int references CLIENTS(id),
          quantity int
);

CREATE TABLE DEVICES (
          UDID varchar(12) primary key UNIQUE,
          MAC varchar(12) UNIQUE,
          version varchar(12) references VERSIONS(hw_type),
          group_id int references GROUPS(id)
);
