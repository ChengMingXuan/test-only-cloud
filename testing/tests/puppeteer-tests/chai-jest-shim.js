/**
 * Chai → Jest expect 兼容 shim
 * 在 Jest 环境中模拟 Chai 的 expect().to.be / .to.have 链式断言
 * 仅覆盖项目中实际使用的断言方法
 */

function createChainableExpect(value) {
  const chain = {
    get to() { return chain; },
    get be() { return chain; },
    get have() { return chain; },
    get that() { return chain; },
    get is() { return chain; },
    get not() {
      return createNegatedChain(value);
    },
    get true() {
      expect(value).toBe(true);
      return chain;
    },
    get false() {
      expect(value).toBe(false);
      return chain;
    },
    get null() {
      expect(value).toBeNull();
      return chain;
    },
    get undefined() {
      expect(value).toBeUndefined();
      return chain;
    },
    get ok() {
      expect(value).toBeTruthy();
      return chain;
    },
    equal(expected) { expect(value).toBe(expected); return chain; },
    eql(expected) { expect(value).toEqual(expected); return chain; },
    deep: {
      equal(expected) { expect(value).toEqual(expected); return chain; },
    },
    greaterThan(n) { expect(value).toBeGreaterThan(n); return chain; },
    lessThan(n) { expect(value).toBeLessThan(n); return chain; },
    above(n) { expect(value).toBeGreaterThan(n); return chain; },
    below(n) { expect(value).toBeLessThan(n); return chain; },
    at: {
      get least() { return (n) => { expect(value).toBeGreaterThanOrEqual(n); return chain; }; },
      get most() { return (n) => { expect(value).toBeLessThanOrEqual(n); return chain; }; },
    },
    include(item) { expect(value).toContain(item); return chain; },
    includes(item) { expect(value).toContain(item); return chain; },
    contain(item) { expect(value).toContain(item); return chain; },
    length(n) { expect(value).toHaveLength(n); return chain; },
    lengthOf(n) { expect(value).toHaveLength(n); return chain; },
    property(prop) { expect(value).toHaveProperty(prop); return chain; },
    match(re) { expect(value).toMatch(re); return chain; },
  };
  return chain;
}

function createNegatedChain(value) {
  return {
    get to() { return this; },
    get be() { return this; },
    get null() { expect(value).not.toBeNull(); return this; },
    get undefined() { expect(value).not.toBeUndefined(); return this; },
    get true() { expect(value).not.toBe(true); return this; },
    get false() { expect(value).not.toBe(false); return this; },
    get ok() { expect(value).toBeFalsy(); return this; },
    equal(expected) { expect(value).not.toBe(expected); return this; },
    include(item) { expect(value).not.toContain(item); return this; },
  };
}

module.exports = { expect: createChainableExpect };
