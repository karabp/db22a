CREATE TABLE organization (
       name VARCHAR(100) NOT NULL,
       type SET('university','company','research-center') NOT NULL,
       acronym VARCHAR(30) NOT NULL,
       address_street VARCHAR(100) NOT NULL,
       address_number VARCHAR(5) NOT NULL,
       address_city VARCHAR(50) NOT NULL,
       address_postal_code VARCHAR(10) NOT NULL,
       public_budget NUMERIC(12,2) NOT NULL,
       private_budget NUMERIC(12,2) NOT NULL,
       PRIMARY KEY (name),       
       CONSTRAINT organization_budget_consistency CHECK (
       		  (NOT type = 'university' OR private_budget = 0) AND
		  (NOT type = 'company' OR public_budget = 0)
       )
);

CREATE TABLE organization_phone (
       organization_name VARCHAR(100) NOT NULL,
       number VARCHAR(30) NOT NULL,
       PRIMARY KEY (organization_name, number),
       CONSTRAINT organization_phone_to_organization_foreign_key FOREIGN KEY (organization_name) REFERENCES organization(name) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE department (
       name VARCHAR(100) NOT NULL,
       PRIMARY KEY (name)
);

CREATE TABLE program (
       name VARCHAR(100) NOT NULL,
       department_name VARCHAR(100) NOT NULL,
       PRIMARY KEY (name, department_name),
       CONSTRAINT program_to_department_foreign_key FOREIGN KEY (department_name) REFERENCES department(name) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE person (
       id INT UNSIGNED NOT NULL AUTO_INCREMENT,
       first_name VARCHAR(50) NOT NULL,
       last_name VARCHAR(50) NOT NULL,
       birth_date DATE NOT NULL,
       sex SET('male','female','non-binary') NOT NULL,
       PRIMARY KEY (id)
);

CREATE TABLE researcher (
       id INT UNSIGNED NOT NULL,
       employing_organization_name VARCHAR(100) NOT NULL,
       employment_start_date DATE NOT NULL,
       PRIMARY KEY (id),
       CONSTRAINT researcher_to_person_foreign_key FOREIGN KEY (id) REFERENCES person(id) ON DELETE CASCADE ON UPDATE CASCADE,
       CONSTRAINT researcher_to_organization_foreign_key FOREIGN KEY (employing_organization_name) REFERENCES organization(name) ON DELETE RESTRICT ON UPDATE CASCADE	       
);

CREATE TABLE manager (
       id INT UNSIGNED NOT NULL,
       PRIMARY KEY (id),
       CONSTRAINT manager_to_person_foreign_key FOREIGN KEY (id) REFERENCES person(id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE project (
       id INT UNSIGNED NOT NULL AUTO_INCREMENT,
       title VARCHAR(200) NOT NULL,
       abstract TEXT NOT NULL,
       funding_amount NUMERIC(9,2) NOT NULL,
       start_date DATE NOT NULL,
       duration INT UNSIGNED NOT NULL,
       reviewer_id INT UNSIGNED NOT NULL,
       review_date DATE NOT NULL,
       review_grade INT UNSIGNED NOT NULL,
       scientific_lead_id INT UNSIGNED NOT NULL,
       manager_id INT UNSIGNED NOT NULL,
       managing_organization_name VARCHAR(100) NOT NULL,
       funding_program_name VARCHAR(100) NOT NULL,
       funding_program_department_name VARCHAR(100) NOT NULL,
       PRIMARY KEY (id),
       CONSTRAINT funding_range CHECK (funding_amount >= 100000 AND funding_amount <= 1000000),
       CONSTRAINT duration_range CHECK (duration >=1*365 AND duration <= 4*365),
       CONSTRAINT review_grade_range CHECK (review_grade >= 5 && review_grade <= 10),
       CONSTRAINT project_to_reviewer_foreign_key FOREIGN KEY (reviewer_id) REFERENCES researcher(id) ON DELETE RESTRICT ON UPDATE CASCADE,
       CONSTRAINT project_to_scientific_lead_foreign_key FOREIGN KEY (scientific_lead_id) REFERENCES researcher(id) ON DELETE RESTRICT ON UPDATE CASCADE,
       CONSTRAINT project_to_manager_foreign_key FOREIGN KEY (manager_id) REFERENCES manager(id) ON DELETE RESTRICT ON UPDATE CASCADE,
       CONSTRAINT project_to_managing_organization_foreign_key FOREIGN KEY (managing_organization_name) REFERENCES organization(name) ON DELETE RESTRICT ON UPDATE CASCADE,
       CONSTRAINT project_to_program_foreign_key FOREIGN KEY (funding_program_name, funding_program_department_name) REFERENCES program(name, department_name) ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE TABLE scientific_field (
       title VARCHAR(100) NOT NULL,
       description TEXT NOT NULL,
       PRIMARY KEY (title)
);    

CREATE TABLE project_relates_to_scientific_field (
       project_id INT UNSIGNED NOT NULL,
       scientific_field_title VARCHAR(100) NOT NULL,
       PRIMARY KEY (project_id, scientific_field_title),
       CONSTRAINT relates_to_project_foreign_key FOREIGN KEY (project_id) REFERENCES project(id) ON DELETE CASCADE ON UPDATE CASCADE,
       CONSTRAINT relates_to_scientific_field_foreign_key FOREIGN KEY (scientific_field_title) REFERENCES scientific_field(title) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE researcher_participates_in_project (
       researcher_id INT UNSIGNED NOT NULL,
       project_id INT UNSIGNED NOT NULL,
       PRIMARY KEY (researcher_id, project_id),
       CONSTRAINT participates_to_researcher_foreign_key FOREIGN KEY (researcher_id) REFERENCES researcher(id) ON DELETE CASCADE ON UPDATE CASCADE,
       CONSTRAINT participates_to_project_foreign_key FOREIGN KEY (project_id) REFERENCES project(id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE deliverable (
       title VARCHAR(200) NOT NULL,
       project_id INT UNSIGNED NOT NULL,
       abstract TEXT NOT NULL,
       delivery_date DATE NOT NULL,
       PRIMARY KEY (title, project_id),
       CONSTRAINT deliverable_to_project_foreign_key FOREIGN KEY (project_id) REFERENCES project(id) ON DELETE CASCADE ON UPDATE CASCADE
)
