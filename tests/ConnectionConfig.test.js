const path = require('path');
const ConnectionConfig = require('../src/models/ConnectionConfig');

describe('ConnectionConfig', () => {
  test('creates with defaults', () => {
    const c = new ConnectionConfig();
    expect(c.filePath).toBe('');
  });

  test('creates with file path', () => {
    const c = new ConnectionConfig({ filePath: './test.db' });
    expect(c.filePath).toBe('./test.db');
  });

  test('resolvedPath returns absolute path', () => {
    const c = new ConnectionConfig({ filePath: './test.db' });
    expect(c.resolvedPath).toBe(path.resolve('./test.db'));
  });

  test('fileName returns basename', () => {
    const c = new ConnectionConfig({ filePath: '/some/dir/mydb.sqlite' });
    expect(c.fileName).toBe('mydb.sqlite');
  });

  test('validate requires file path', () => {
    const c = new ConnectionConfig();
    const errors = c.validate();
    expect(errors).toContain('Database file path is required');
  });

  test('validate rejects non-existent directory', () => {
    const c = new ConnectionConfig({ filePath: '/nonexistent_dir_xyz/test.db' });
    const errors = c.validate();
    expect(errors.some(e => e.includes('Directory does not exist'))).toBe(true);
  });

  test('validate passes for valid path', () => {
    const c = new ConnectionConfig({ filePath: './test.db' });
    expect(c.validate()).toEqual([]);
  });
});
