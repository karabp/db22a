CREATE VIEW dual_role_people AS
       SELECT person.id,
       	      person.first_name,
	      person.last_name,
	      person.birth_date,
	      researcher.employing_organization_name,
     	      COUNT(DISTINCT manager_project.id) AS managing_project_number,
	      COUNT(DISTINCT participates.project_id) AS participating_project_number,
       	      COUNT(DISTINCT lead_project.id) AS leading_project_number,
       	      COUNT(DISTINCT reviewer_project.id) AS reviewing_project_number
       FROM person
       INNER JOIN researcher
       INNER JOIN manager
       ON person.id = manager.id
       AND person.id = researcher.id
       LEFT OUTER JOIN project AS manager_project
       ON manager_project.manager_id = manager.id
       LEFT OUTER JOIN project AS lead_project
       ON lead_project.scientific_lead_id = researcher.id
       LEFT OUTER JOIN project AS reviewer_project
       ON reviewer_project.reviewer_id = researcher.id
       LEFT OUTER JOIN researcher_participates_in_project AS participates
       ON participates.researcher_id = researcher.id
       GROUP BY person.id
       ORDER BY person.last_name ASC, person.first_name ASC
