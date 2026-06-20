const ConnectionController = require('../src/controllers/ConnectionController');
const QueryController = require('../src/controllers/QueryController');

function mockReq(body = {}) {
  return { body };
}

function mockRes() {
  const res = {};
  res.status = jest.fn().mockReturnValue(res);
  res.json = jest.fn().mockReturnValue(res);
  return res;
}

describe('ConnectionController', () => {
  test('status returns not connected by default', () => {
    const req = mockReq();
    const res = mockRes();
    ConnectionController.status(req, res);
    expect(res.json).toHaveBeenCalledWith(
      expect.objectContaining({ connected: false })
    );
  });

  test('connect rejects empty file path', async () => {
    const req = mockReq({ filePath: '' });
    const res = mockRes();
    await ConnectionController.connect(req, res);
    expect(res.status).toHaveBeenCalledWith(400);
    expect(res.json).toHaveBeenCalledWith(
      expect.objectContaining({ success: false })
    );
  });
});

describe('QueryController', () => {
  test('buildQuery returns SQL', () => {
    const req = mockReq({
      columns: [{ expression: '*', alias: '' }],
      from: { table: 'TestTable', alias: 't' },
    });
    const res = mockRes();
    QueryController.buildQuery(req, res);
    expect(res.json).toHaveBeenCalledWith(
      expect.objectContaining({
        success: true,
        sql: expect.stringContaining('TestTable'),
      })
    );
  });

  test('buildQuery rejects missing body', () => {
    const req = { body: null };
    const res = mockRes();
    QueryController.buildQuery(req, res);
    expect(res.status).toHaveBeenCalledWith(400);
  });

  test('getJoinTypes returns types', () => {
    const req = mockReq();
    const res = mockRes();
    QueryController.getJoinTypes(req, res);
    expect(res.json).toHaveBeenCalledWith(
      expect.objectContaining({ joinTypes: expect.any(Array) })
    );
  });

  test('resetQuery clears builder', () => {
    const req = mockReq();
    const res = mockRes();
    QueryController.resetQuery(req, res);
    expect(res.json).toHaveBeenCalledWith(
      expect.objectContaining({ success: true })
    );
  });
});
