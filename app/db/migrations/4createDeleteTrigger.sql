CREATE OR REPLACE FUNCTION delete_children_folder() RETURNS trigger AS $delete_children_folder$
    BEGIN
        DELETE FROM folder WHERE parentId = OLD.id;
        DELETE FROM history WHERE ItemId = OLD.id;
        RETURN NEW;
    END;

$delete_children_folder$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER delete_children_folder AFTER DELETE
    ON folder
    FOR ROW
    EXECUTE FUNCTION delete_children_folder();


CREATE OR REPLACE FUNCTION delete_children_file() RETURNS trigger AS $delete_children_file$
    BEGIN
        DELETE FROM history WHERE ItemId = OLD.id;
        RETURN NEW;
    END;

$delete_children_file$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER delete_children_file AFTER DELETE
    ON file
    FOR ROW
    EXECUTE FUNCTION delete_children_file();