-- Триггер для обновления даты в родительских папках после обновления файла.
-- Добавляет в историю запись после обновления.
CREATE OR REPLACE FUNCTION update_dates_update_file() RETURNS trigger AS $update_dates_update_file$
    BEGIN
        UPDATE folder set date = NEW.date WHERE id = NEW.parentId OR id = OLD.parentId;
        INSERT INTO history (ItemId, Url, Date, ParentId, Size, Type) VALUES
            (NEW.Id, NEW.Url, NEW.Date, NEW.ParentId, NEW.Size, 'FILE');
        RETURN NEW;
    END;

$update_dates_update_file$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER update_data_file AFTER UPDATE
    ON file
    FOR ROW
    EXECUTE FUNCTION update_dates_update_file();


-- Триггер, который перед обновлением папки собирает стоимости дочерних папок и файлов и складывает их.
CREATE OR REPLACE FUNCTION update_price_folder() RETURNS trigger AS $update_price_update_folder$
    DECLARE
        folders_sum integer;
        files_sum integer;
        file_item file;
        folder_item folder;
    BEGIN
        files_sum := 0;
        FOR file_item IN SELECT * FROM file WHERE parentId = NEW.id
            LOOP
                IF file_item.size IS NOT NULL THEN
                    files_sum := files_sum + file_item.size;
                END IF;
            END LOOP;

        folders_sum := 0;
        FOR folder_item IN SELECT * FROM folder WHERE parentId = NEW.id
            LOOP
                IF folder_item.size IS NOT NULL THEN
                    folders_sum := folders_sum + folder_item.size;
                END IF;
            END LOOP;
        NEW.size = folders_sum + files_sum;
        RETURN NEW;
    END;

$update_price_update_folder$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER update_price_folder_trigger BEFORE UPDATE
    ON folder
    FOR ROW
    EXECUTE FUNCTION update_price_folder();

-- Триггер, который после обновления папки, обновляет все родительские папки.
CREATE OR REPLACE FUNCTION update_dates_folder() RETURNS trigger AS $update_dates_folder$
    BEGIN
        UPDATE folder set date = NEW.date WHERE id = NEW.parentId OR id = OLD.parentId;
        IF (NEW.Date = OLD.Date) THEN
            UPDATE history SET
            Url=NEW.Url, ParentId=NEW.ParentId, Size=NEW.Size WHERE ItemId = NEW.Id AND Date = NEW.Date;
        ELSE
            INSERT INTO history (ItemId, Url, Date, ParentId, Size, Type) VALUES
                (NEW.Id, NEW.Url, NEW.Date, NEW.ParentId, NEW.Size, 'FOLDER');
        END IF;
        RETURN NEW;
    END;

$update_dates_folder$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER update_date_folder AFTER UPDATE
    ON folder
    FOR ROW
    EXECUTE FUNCTION update_dates_folder();