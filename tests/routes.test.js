const connectionRoutes = require('../src/routes/connectionRoutes');
const schemaRoutes = require('../src/routes/schemaRoutes');
const queryRoutes = require('../src/routes/queryRoutes');

describe('Route modules', () => {
  test('connectionRoutes is a valid router', () => {
    expect(connectionRoutes).toBeDefined();
    expect(typeof connectionRoutes).toBe('function');
    expect(connectionRoutes.stack).toBeInstanceOf(Array);
    expect(connectionRoutes.stack.length).toBeGreaterThan(0);
  });

  test('schemaRoutes is a valid router', () => {
    expect(schemaRoutes).toBeDefined();
    expect(typeof schemaRoutes).toBe('function');
    expect(schemaRoutes.stack).toBeInstanceOf(Array);
    expect(schemaRoutes.stack.length).toBeGreaterThan(0);
  });

  test('queryRoutes is a valid router', () => {
    expect(queryRoutes).toBeDefined();
    expect(typeof queryRoutes).toBe('function');
    expect(queryRoutes.stack).toBeInstanceOf(Array);
    expect(queryRoutes.stack.length).toBeGreaterThan(0);
  });

  test('connectionRoutes has POST /connect', () => {
    const route = connectionRoutes.stack.find(r =>
      r.route && r.route.path === '/connect' && r.route.methods.post
    );
    expect(route).toBeDefined();
  });

  test('connectionRoutes has GET /status', () => {
    const route = connectionRoutes.stack.find(r =>
      r.route && r.route.path === '/status' && r.route.methods.get
    );
    expect(route).toBeDefined();
  });

  test('schemaRoutes has GET /tables', () => {
    const route = schemaRoutes.stack.find(r =>
      r.route && r.route.path === '/tables' && r.route.methods.get
    );
    expect(route).toBeDefined();
  });

  test('queryRoutes has POST /build', () => {
    const route = queryRoutes.stack.find(r =>
      r.route && r.route.path === '/build' && r.route.methods.post
    );
    expect(route).toBeDefined();
  });

  test('queryRoutes has POST /execute', () => {
    const route = queryRoutes.stack.find(r =>
      r.route && r.route.path === '/execute' && r.route.methods.post
    );
    expect(route).toBeDefined();
  });
});
