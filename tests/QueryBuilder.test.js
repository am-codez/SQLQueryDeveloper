const QueryBuilder = require('../src/models/QueryBuilder');

describe('QueryBuilder', () => {
  let qb;

  beforeEach(() => {
    qb = new QueryBuilder();
  });

  test('builds basic SELECT', () => {
    qb.addColumn('*');
    qb.setFrom('Users', 'u');
    const sql = qb.build();
    expect(sql).toContain('SELECT');
    expect(sql).toContain('*');
    expect(sql).toContain('FROM Users AS u');
  });

  test('builds SELECT with specific columns', () => {
    qb.addColumn('u.id');
    qb.addColumn('u.name', 'UserName');
    qb.setFrom('Users', 'u');
    const sql = qb.build();
    expect(sql).toContain('u.id');
    expect(sql).toContain('u.name AS UserName');
  });

  test('builds SELECT TOP', () => {
    qb.setTop(100);
    qb.addColumn('*');
    qb.setFrom('Orders');
    const sql = qb.build();
    expect(sql).toContain('SELECT TOP (100)');
  });

  test('builds JOIN', () => {
    qb.addColumn('*');
    qb.setFrom('Users', 'u');
    qb.addJoin('Orders', 'INNER JOIN', 'o', 'u.id = o.user_id');
    const sql = qb.build();
    expect(sql).toContain('INNER JOIN Orders');
    expect(sql).toContain('AS o');
    expect(sql).toContain('ON u.id = o.user_id');
  });

  test('builds WHERE equality', () => {
    qb.addColumn('*');
    qb.setFrom('Users');
    qb.addWhereEquality('u.status', '=', "'active'");
    const sql = qb.build();
    expect(sql).toContain('WHERE');
    expect(sql).toContain("u.status = 'active'");
  });

  test('builds WHERE between', () => {
    qb.addColumn('*');
    qb.setFrom('Orders');
    qb.addWhereBetween('o.date', 'BETWEEN', "'2024-01-01'", "'2024-12-31'");
    const sql = qb.build();
    expect(sql).toContain("o.date BETWEEN '2024-01-01' AND '2024-12-31'");
  });

  test('builds WHERE null', () => {
    qb.addColumn('*');
    qb.setFrom('Users');
    qb.addWhereNull('u.deleted_at', 'IS NULL');
    const sql = qb.build();
    expect(sql).toContain('u.deleted_at IS NULL');
  });

  test('builds GROUP BY', () => {
    qb.addColumn('u.city');
    qb.addColumn('COUNT(*)', 'cnt');
    qb.setFrom('Users', 'u');
    qb.setGroupBy(['u.city'], 'ASC');
    const sql = qb.build();
    expect(sql).toContain('GROUP BY u.city ASC');
  });

  test('builds HAVING', () => {
    qb.addColumn('u.city');
    qb.addColumn('COUNT(*)', 'cnt');
    qb.setFrom('Users', 'u');
    qb.setGroupBy(['u.city'], 'ASC');
    qb.setHaving('cnt', '>', 5);
    const sql = qb.build();
    expect(sql).toContain('HAVING COUNT(cnt) > 5');
  });

  test('builds ORDER BY', () => {
    qb.addColumn('*');
    qb.setFrom('Users');
    qb.setOrderBy(['u.created_at'], 'DESC');
    const sql = qb.build();
    expect(sql).toContain('ORDER BY u.created_at DESC');
  });

  test('builds UNION', () => {
    qb.addColumn('name');
    qb.setFrom('Employees');

    const unionQb = new QueryBuilder();
    unionQb.addColumn('name');
    unionQb.setFrom('Contractors');
    qb.setUnion(unionQb);

    const sql = qb.build();
    expect(sql).toContain('Employees');
    expect(sql).toContain('Contractors');
  });

  test('builds complex query with all clauses', () => {
    qb.setTop(50);
    qb.addColumn('o.id');
    qb.addColumn('o.total');
    qb.addColumn('u.name');
    qb.setFrom('Orders', 'o');
    qb.addJoin('Users', 'INNER JOIN', 'u', 'o.user_id = u.id');
    qb.addWhereEquality('u.status', '=', "'active'");
    qb.setGroupBy(['u.name'], 'ASC');
    qb.setHaving('o.total', '>', 100);
    qb.setOrderBy(['o.total'], 'DESC');

    const sql = qb.build();
    expect(sql).toContain('SELECT TOP (50)');
    expect(sql).toContain('FROM Orders AS o');
    expect(sql).toContain('INNER JOIN Users AS u');
    expect(sql).toContain('ON o.user_id = u.id');
    expect(sql).toContain("WHERE u.status = 'active'");
    expect(sql).toContain('GROUP BY u.name ASC');
    expect(sql).toContain('HAVING COUNT(o.total) > 100');
    expect(sql).toContain('ORDER BY o.total DESC');
  });

  test('WhereClause with multiple conditions', () => {
    const w = new QueryBuilder.WhereClause();
    w.addEquality('a', '=', '1');
    w.addEquality('b', '>', '2');
    w.addNull('c', 'IS NULL');
    const str = w.toString();
    expect(str).toContain('WHERE');
    expect(str).toContain('a = 1');
    expect(str).toContain('b > 2');
    expect(str).toContain('c IS NULL');
  });

  test('reset clears everything', () => {
    qb.addColumn('*');
    qb.setFrom('Users');
    qb.reset();
    expect(qb.columns).toEqual([]);
    expect(qb.fromTable).toBe('');
    const sql = qb.build();
    expect(sql).toContain('SELECT');
  });
});
