CREATE TRIGGER project_reviewer_cannot_work_for_managing_organization
BEFORE INSERT ON project
FOR EACH ROW
BEGIN
	IF (NEW.managing_organization_name =
	   (SELECT name
	    FROM organization
	    INNER JOIN researcher
	    ON researcher.employing_organization_name = organization.name
	    WHERE researcher.id = NEW.reviewer_id))
	THEN
		SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'A project reviewer may not work for the project managing organization.';
	END IF;
END;
