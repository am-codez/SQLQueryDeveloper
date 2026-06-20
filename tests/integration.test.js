const QueryBuilderService = require('../src/services/QueryBuilderService');

describe('Integration: QueryBuilderService + QueryBuilder model', () => {
  test('full query lifecycle: build, getSQL, reset', () => {
    const service = new QueryBuilderService();

    service.buildQueryFromSteps({
      columns: [{ expression: 'p.id', alias: '' }, { expression: 'p.name', alias: 'ProductName' }],
      from: { table: 'Products', alias: 'p' },
      joins: [{ type: 'LEFT JOIN', table: 'Categories', alias: 'c', on: 'p.category_id = c.id' }],
      where: [{ type: 'equality', column: 'p.price', operator: '>', value: '10' }],
      orderBy: { columns: ['ProductName'], direction: 'ASC' },
    });

    const sql = service.getSQL();
    expect(sql).toContain('SELECT');
    expect(sql).toContain('p.name AS ProductName');
    expect(sql).toContain('FROM Products AS p');
    expect(sql).toContain('LEFT JOIN Categories AS c');
    expect(sql).toContain('ON p.category_id = c.id');
    expect(sql).toContain('WHERE p.price > 10');
    expect(sql).toContain('ORDER BY ProductName ASC');

    service.reset();
    const sql2 = service.getSQL();
    expect(sql2).not.toContain('Products');
  });

  test('multiple sequential builds', () => {
    const service = new QueryBuilderService();

    service.buildQueryFromSteps({
      columns: [{ expression: '*', alias: '' }],
      from: { table: 'TableA', alias: 'a' },
    });
    expect(service.getSQL()).toContain('TableA');

    service.buildQueryFromSteps({
      columns: [{ expression: '*', alias: '' }],
      from: { table: 'TableB', alias: 'b' },
    });
    expect(service.getSQL()).toContain('TableB');
    expect(service.getSQL()).not.toContain('TableA');
  });

  test('complex nested query generation', () => {
    const service = new QueryBuilderService();
    service.buildQueryFromSteps({
      top: 10,
      columns: [
        { expression: 'o.id', alias: 'OrderID' },
        { expression: 'o.amount', alias: '' },
        { expression: 'c.name', alias: 'Customer' },
      ],
      from: { table: 'Orders', alias: 'o' },
      joins: [
        { type: 'INNER JOIN', table: 'Customers', alias: 'c', on: 'o.customer_id = c.id' },
      ],
      where: [
        { type: 'equality', column: 'o.status', operator: '=', value: "'completed'", logical: 'AND' },
        { type: 'null', column: 'o.refund_date', operator: 'IS NULL', logical: 'AND' },
      ],
      groupBy: { columns: ['o.id', 'c.name'], order: 'DESC' },
      having: { column: 'o.amount', operator: '>', value: 0 },
      orderBy: { columns: ['o.amount'], direction: 'DESC' },
    });

    const sql = service.getSQL();
    expect(sql).toContain('SELECT TOP (10)');
    expect(sql).toContain('o.id AS OrderID');
    expect(sql).toContain('o.amount');
    expect(sql).toContain('c.name AS Customer');
    expect(sql).toContain('FROM Orders AS o');
    expect(sql).toContain('INNER JOIN Customers AS c');
    expect(sql).toContain("WHERE o.status = 'completed'");
    expect(sql).toContain('o.refund_date IS NULL');
    expect(sql).toContain('GROUP BY o.id, c.name DESC');
    expect(sql).toContain('HAVING COUNT(o.amount) > 0');
    expect(sql).toContain('ORDER BY o.amount DESC');
  });
});
