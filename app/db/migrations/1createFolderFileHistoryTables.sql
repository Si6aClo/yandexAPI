CREATE TABLE folder(
    Id uuid unique,
    Url varchar(255),
    Date timestamp,
    ParentId uuid,
    Size int
);

CREATE TABLE file(
    Id uuid unique,
    Url varchar(255),
    Date timestamp,
    ParentId uuid,
    Size int,
    FOREIGN KEY (ParentId) REFERENCES Folder (Id) ON DELETE CASCADE
);

CREATE TABLE history(
    Id serial primary key,
    ItemId uuid,
    Url varchar(255),
    Date timestamp,
    ParentId uuid,
    Size int,
    Type varchar(16)
);