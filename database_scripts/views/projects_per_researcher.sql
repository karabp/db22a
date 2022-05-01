CREATE VIEW projects_per_researcher AS
       SELECT researcher_id,
       	      person.first_name,
	      person.last_name,
	      person.birth_date,
	      COUNT(project.id) AS project_number,
	      GROUP_CONCAT(project.title) AS project_titles
       FROM researcher_participates_in_project
       INNER JOIN researcher
       INNER JOIN project
       INNER JOIN person
       ON researcher.id = researcher_id
       AND person.id = researcher_id
       AND project.id = project_id
       GROUP BY researcher_id
       ORDER BY COUNT(project.id) DESC
