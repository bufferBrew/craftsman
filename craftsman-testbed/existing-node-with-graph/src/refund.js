const { applyDiscount } = require('./payment');

function refundAmount(amount) {
  // reuses the same buggy applyDiscount() truncation from payment.js
  return applyDiscount(amount);
}

module.exports = { refundAmount };
