-- Seed data for local development and SAST testing
-- 3 orgs, 10 users, 20 projects, 50+ tasks

INSERT INTO orgs (id, name, owner_id) VALUES
  (1, 'Acme Corp', NULL),
  (2, 'StartupXYZ', NULL),
  (3, 'DevTeam Inc', NULL);

-- passwords are bcrypt hash of 'Password123!' (rounds=10)
INSERT INTO users (id, email, password_hash, full_name, role, org_id) VALUES
  (1, 'admin@acme.com', '$2b$10$rQnM1.Hx5YqKvGZ5YqKvGe5YqKvGZ5YqKvGZ5YqKvGZ5YqKvGZ5YqK', 'Admin User', 'admin', 1),
  (2, 'alice@acme.com', '$2b$10$rQnM1.Hx5YqKvGZ5YqKvGe5YqKvGZ5YqKvGZ5YqKvGZ5YqKvGZ5YqK', 'Alice Smith', 'member', 1),
  (3, 'bob@acme.com', '$2b$10$rQnM1.Hx5YqKvGZ5YqKvGe5YqKvGZ5YqKvGZ5YqKvGZ5YqKvGZ5YqK', 'Bob Jones', 'member', 1),
  (4, 'carol@startup.xyz', '$2b$10$rQnM1.Hx5YqKvGZ5YqKvGe5YqKvGZ5YqKvGZ5YqKvGZ5YqKvGZ5YqK', 'Carol Lee', 'admin', 2),
  (5, 'dave@startup.xyz', '$2b$10$rQnM1.Hx5YqKvGZ5YqKvGe5YqKvGZ5YqKvGZ5YqKvGZ5YqKvGZ5YqK', 'Dave Wilson', 'member', 2),
  (6, 'eve@devteam.com', '$2b$10$rQnM1.Hx5YqKvGZ5YqKvGe5YqKvGZ5YqKvGZ5YqKvGZ5YqKvGZ5YqK', 'Eve Brown', 'admin', 3),
  (7, 'frank@devteam.com', '$2b$10$rQnM1.Hx5YqKvGZ5YqKvGe5YqKvGZ5YqKvGZ5YqKvGZ5YqKvGZ5YqKvGZ5YqK', 'Frank Davis', 'member', 3),
  (8, 'grace@acme.com', '$2b$10$rQnM1.Hx5YqKvGZ5YqKvGe5YqKvGZ5YqKvGZ5YqKvGZ5YqKvGZ5YqKvGZ5YqK', 'Grace Miller', 'member', 1),
  (9, 'henry@startup.xyz', '$2b$10$rQnM1.Hx5YqKvGZ5YqKvGe5YqKvGZ5YqKvGZ5YqKvGZ5YqKvGZ5YqKvGZ5YqK', 'Henry Clark', 'member', 2),
  (10, 'ivy@devteam.com', '$2b$10$rQnM1.Hx5YqKvGZ5YqKvGe5YqKvGZ5YqKvGZ5YqKvGZ5YqKvGZ5YqKvGZ5YqK', 'Ivy White', 'member', 3);

UPDATE orgs SET owner_id = 1 WHERE id = 1;
UPDATE orgs SET owner_id = 4 WHERE id = 2;
UPDATE orgs SET owner_id = 6 WHERE id = 3;

INSERT INTO org_members (org_id, user_id, role) VALUES
  (1, 1, 'admin'), (1, 2, 'member'), (1, 3, 'member'), (1, 8, 'member'),
  (2, 4, 'admin'), (2, 5, 'member'), (2, 9, 'member'),
  (3, 6, 'admin'), (3, 7, 'member'), (3, 10, 'member');

INSERT INTO projects (id, org_id, name, description) VALUES
  (1, 1, 'Website Redesign', 'Public site refresh Q1'),
  (2, 1, 'API v2', 'REST API migration'),
  (3, 1, 'Mobile App', 'iOS and Android'),
  (4, 1, 'DevOps Pipeline', 'CI/CD improvements'),
  (5, 1, 'Security Audit', 'Annual pen test prep'),
  (6, 2, 'MVP Launch', 'First product release'),
  (7, 2, 'Marketing Site', 'Landing and blog'),
  (8, 2, 'Backend Services', 'Microservices'),
  (9, 2, 'Analytics Dashboard', 'User metrics'),
  (10, 2, 'Integrations', 'Third-party APIs'),
  (11, 3, 'Platform Core', 'Core platform features'),
  (12, 3, 'Billing System', 'Stripe integration'),
  (13, 3, 'Support Portal', 'Customer support'),
  (14, 3, 'Internal Tools', 'Admin and ops'),
  (15, 3, 'Documentation', 'Developer docs'),
  (16, 1, 'Legacy Migration', 'Monolith to services'),
  (17, 2, 'Data Pipeline', 'ETL and reporting'),
  (18, 3, 'Mobile SDK', 'Client libraries'),
  (19, 1, 'QA Automation', 'E2E tests'),
  (20, 2, 'Customer Onboarding', 'Signup flows');

INSERT INTO tasks (project_id, title, description, status, assignee_id, priority, due_date, created_by) VALUES
  (1, 'Design homepage mockups', 'Figma frames for new homepage', 'open', 2, 'high', '2025-04-01', 1),
  (1, 'Implement header component', 'Responsive nav with dropdown', 'in_progress', 2, 'medium', '2025-03-15', 1),
  (1, 'Content copy review', 'Legal and marketing review', 'open', 8, 'low', NULL, 1),
  (2, 'Define API spec', 'OpenAPI 3.0 document', 'done', 3, 'high', '2025-03-01', 1),
  (2, 'Auth middleware', 'JWT validation and rate limit', 'in_progress', 3, 'high', '2025-03-20', 1),
  (2, 'Pagination for list endpoints', 'Cursor-based pagination', 'open', 3, 'medium', NULL, 1),
  (3, 'Splash screen', 'Animated logo and loading', 'open', 7, 'medium', '2025-04-10', 6),
  (3, 'Push notification setup', 'FCM and APNs', 'open', 7, 'high', '2025-04-05', 6),
  (4, 'Dockerize backend', 'Multi-stage build', 'done', 3, 'high', '2025-02-28', 1),
  (4, 'K8s deployment manifests', 'Staging and prod', 'in_progress', 1, 'high', '2025-03-25', 1),
  (5, 'Dependency audit', 'npm audit and fix', 'open', 1, 'medium', '2025-03-30', 1),
  (5, 'OWASP checklist', 'Address ZAP findings', 'open', 3, 'high', NULL, 1),
  (6, 'User registration flow', 'Email verification', 'in_progress', 4, 'high', '2025-03-18', 4),
  (6, 'Payment integration', 'Stripe Checkout', 'open', 5, 'high', '2025-04-01', 4),
  (7, 'Hero section', 'Headline and CTA', 'done', 5, 'high', '2025-03-10', 4),
  (7, 'Blog listing page', 'Paginated posts', 'open', 9, 'medium', NULL, 4),
  (8, 'User service', 'CRUD and auth', 'in_progress', 5, 'high', '2025-03-22', 4),
  (8, 'Task service', 'Projects and tasks', 'in_progress', 5, 'high', '2025-03-22', 4),
  (9, 'Event tracking schema', 'Identify key events', 'open', 9, 'medium', '2025-03-28', 4),
  (10, 'Slack webhook', 'Notifications to Slack', 'open', 9, 'low', NULL, 4),
  (11, 'Tenant isolation', 'Row-level security', 'in_progress', 6, 'high', '2025-03-20', 6),
  (11, 'API versioning', 'v1 prefix and deprecation', 'open', 7, 'medium', NULL, 6),
  (12, 'Subscription plans', 'Free / Pro / Enterprise', 'in_progress', 6, 'high', '2025-04-05', 6),
  (12, 'Webhook delivery', 'Retry and logging', 'open', 10, 'medium', NULL, 6),
  (13, 'Ticket form', 'Category and priority', 'open', 10, 'medium', '2025-03-25', 6),
  (13, 'Knowledge base', 'Search and categories', 'open', 10, 'low', NULL, 6),
  (14, 'User management UI', 'Admin table and filters', 'in_progress', 7, 'high', '2025-03-25', 6),
  (14, 'Audit log export', 'CSV and date range', 'open', 7, 'low', NULL, 6),
  (15, 'API reference', 'Auto-generated from OpenAPI', 'open', 10, 'medium', '2025-04-01', 6),
  (16, 'Extract auth service', 'First microservice', 'open', 1, 'high', NULL, 1),
  (17, 'Daily aggregation job', 'BigQuery sync', 'open', 5, 'medium', '2025-03-30', 4),
  (18, 'iOS SDK', 'Swift package', 'open', 7, 'high', '2025-04-15', 6),
  (19, 'Login E2E', 'Playwright test', 'in_progress', 2, 'medium', '2025-03-20', 1),
  (20, 'Welcome email sequence', 'Drip campaign', 'open', 9, 'medium', NULL, 4);

INSERT INTO task_comments (task_id, user_id, body) VALUES
  (1, 1, 'Please use the new brand colors from Figma.'),
  (2, 2, 'Almost done, will push by EOD.'),
  (4, 3, 'Spec approved by team.'),
  (6, 4, 'We should add webhook support in v2.');

INSERT INTO notifications (user_id, type, payload) VALUES
  (2, 'task_assigned', '{"taskId": 1, "taskTitle": "Design homepage mockups"}'),
  (3, 'mention', '{"taskId": 2, "from": "Admin User"}');

SELECT setval('orgs_id_seq', 20);
SELECT setval('users_id_seq', 10);
SELECT setval('projects_id_seq', 20);
SELECT setval('tasks_id_seq', 100);
