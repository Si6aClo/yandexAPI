-- Триггер, обновляющий дату в родительских папках после создания текущего файла.
-- Также записывает значение в history.
CREATE OR REPLACE FUNCTION update_dates_insert_file() RETURNS trigger AS $update_dates_insert_file$
    BEGIN
        UPDATE folder set date = NEW.date WHERE id = NEW.parentId;
        INSERT INTO history (ItemId, Url, Date, ParentId, Size, Type) VALUES
            (NEW.Id, NEW.Url, NEW.Date, NEW.ParentId, NEW.Size, 'FILE');
        RETURN NEW;
    END;

$update_dates_insert_file$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER insert_data_file AFTER INSERT
    ON file
    FOR ROW
    EXECUTE FUNCTION update_dates_insert_file();


-- Триггер, обновляющий дату в родительских папках после создания текущей.
-- Также записывает значение в history.
CREATE OR REPLACE FUNCTION update_dates_insert_folder() RETURNS trigger AS $update_dates_insert_folder$
    BEGIN
        UPDATE folder set date = NEW.date WHERE id = NEW.parentId;
        INSERT INTO history (ItemId, Url, Date, ParentId, Size, Type) VALUES
            (NEW.Id, NEW.Url, NEW.Date, NEW.ParentId, NEW.Size, 'FOLDER');
        RETURN NEW;
    END;

$update_dates_insert_folder$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER insert_data_folder AFTER INSERT
    ON folder
    FOR ROW
    EXECUTE FUNCTION update_dates_insert_folder();