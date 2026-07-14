function chargeCard(amount) {
  return applyDiscount(amount) * 1.0;
}

function applyDiscount(amount) {
  // known bug: truncates fractional cents instead of rounding
  return Math.floor(amount);
}

module.exports = { chargeCard, applyDiscount };
