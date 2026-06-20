const QueryBuilderService = require('../src/services/QueryBuilderService');

describe('QueryBuilderService', () => {
  let service;

  beforeEach(() => {
    service = new QueryBuilderService();
  });

  test('builds query from steps object', () => {
    service.buildQueryFromSteps({
      columns: [{ expression: '*', alias: '' }],
      from: { table: 'Users', alias: 'u' },
    });
    const sql = service.getSQL();
    expect(sql).toContain('SELECT');
    expect(sql).toContain('*');
    expect(sql).toContain('FROM Users AS u');
  });

  test('builds query with all clauses from steps', () => {
    service.buildQueryFromSteps({
      top: 100,
      columns: [
        { expression: 'u.id', alias: '' },
        { expression: 'u.name', alias: 'UserName' },
        { expression: 'COUNT(*)', alias: 'order_count' },
      ],
      from: { table: 'Users', alias: 'u' },
      joins: [
        { type: 'INNER JOIN', table: 'Orders', alias: 'o', on: 'u.id = o.user_id' },
      ],
      where: [
        { type: 'equality', column: 'u.status', operator: '=', value: "'active'", logical: 'AND' },
        { type: 'null', column: 'u.deleted_at', operator: 'IS NULL', logical: 'AND' },
      ],
      groupBy: { columns: ['u.id', 'u.name'], order: 'ASC' },
      having: { column: 'u.id', operator: '>', value: 5 },
      orderBy: { columns: ['order_count'], direction: 'DESC' },
    });

    const sql = service.getSQL();
    expect(sql).toContain('SELECT TOP (100)');
    expect(sql).toContain('u.name AS UserName');
    expect(sql).toContain('FROM Users AS u');
    expect(sql).toContain('INNER JOIN Orders AS o');
    expect(sql).toContain('ON u.id = o.user_id');
    expect(sql).toContain("WHERE u.status = 'active'");
    expect(sql).toContain('u.deleted_at IS NULL');
    expect(sql).toContain('GROUP BY u.id, u.name ASC');
    expect(sql).toContain('HAVING COUNT(u.id) > 5');
    expect(sql).toContain('ORDER BY order_count DESC');
  });

  test('builds UNION query from steps', () => {
    service.buildQueryFromSteps({
      columns: [{ expression: 'name', alias: '' }],
      from: { table: 'Employees', alias: '' },
      union: {
        columns: [{ expression: 'name', alias: '' }],
        from: { table: 'Contractors', alias: '' },
      },
    });

    const sql = service.getSQL();
    expect(sql).toContain('Employees');
    expect(sql).toContain('Contractors');
  });

  test('reset clears the builder', () => {
    service.buildQueryFromSteps({
      columns: [{ expression: '*', alias: '' }],
      from: { table: 'Users', alias: '' },
    });
    service.reset();
    const sql = service.getSQL();
    expect(sql).not.toContain('Users');
  });

  test('empty steps produces minimal query', () => {
    service.buildQueryFromSteps({});
    const sql = service.getSQL();
    expect(sql).toContain('SELECT');
  });

  test('returns available join types', () => {
    const types = service.getJoinTypes();
    expect(types).toContain('JOIN');
    expect(types).toContain('INNER JOIN');
    expect(types).toContain('LEFT JOIN');
    expect(types).toContain('CROSS JOIN');
  });

  test('returns available comparison operators', () => {
    const ops = service.getComparisonOps();
    expect(ops).toContain('=');
    expect(ops).toContain('LIKE');
    expect(ops).toContain('IN');
  });
});
