-- DATA
delete from scheduled_search;
delete from search_report;
delete from menu_report;
delete from subscription;
delete from chat;
delete from menu;
delete from restaurant;

-- restaurant
INSERT INTO restaurant values (0, 'Bar Primero', 666666666, 'https://github.com/asaezper/dagan', 39.474811, -0.358192);
INSERT INTO restaurant values (1, 'Bar Segundo', 666666666, 'https://github.com/asaezper/dagan', 39.474811, -0.358192);
INSERT INTO restaurant values (2, 'Bar Tercero', 666666666, 'https://github.com/asaezper/dagan', 39.474811, -0.358192);

-- menu
INSERT INTO menu values (0, 0, 'Ensaladas');
INSERT INTO menu values (1, 0, 'Menú del día');
INSERT INTO menu values (2, 0, 'Menú del día');
INSERT INTO menu values (2, 1, 'Bocatas del día');
INSERT INTO menu values (2, 2, 'Tardeos');
INSERT INTO menu values (2, 3, 'Menú ensalada');

commit;
