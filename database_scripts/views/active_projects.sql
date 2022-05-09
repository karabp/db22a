CREATE VIEW active_project AS
       (SELECT project.*
        FROM project
	WHERE ADDDATE(project.start_date, project.duration) >= CURRENT_DATE()
       )
