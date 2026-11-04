"use strict";
const form = document.getElementById("cost-form");
function calculateCost() {
  const ids = ["input-tokens", "cached-tokens", "write-tokens", "output-tokens"];
  const nodes = ids.map(id => document.getElementById(id));
  const values = nodes.map(node => Number(node.value));
  const valid = nodes.every((node, i) => node.value.trim() !== "" && Number.isFinite(values[i]) && values[i] >= 0 && values[i] <= 10000000);
  document.getElementById("cost-value").textContent = valid ? "$" + ((values[0] * 2 + values[1] * 0.2 + values[2] * 2 + values[3] * 10) / 1000000).toFixed(4) : "Check inputs";
}
form.addEventListener("input", calculateCost);
form.addEventListener("submit", event => event.preventDefault());
calculateCost();
let fixed = false;
document.getElementById("demo-button").addEventListener("click", () => {
  fixed = !fixed;
  document.getElementById("demo-code").textContent = fixed ? "-    return a - b\n+    return a + b\n\nExpected result: add(2, 3) = 5" : "def add(a, b):\n    return a - b";
  document.getElementById("demo-status").textContent = fixed ? "Fixture patch shown. Run the Python demo locally to execute the actual before-and-after test." : "Test expects add(2, 3) = 5. The current result is -1.";
  document.getElementById("demo-button").textContent = fixed ? "Reset the walkthrough" : "Show the fixture fix";
});
document.querySelectorAll("[data-copy]").forEach(button => button.addEventListener("click", async () => {
  const code = document.getElementById(button.dataset.copy).textContent;
  try {
    await navigator.clipboard.writeText(code);
    document.getElementById("copy-status").textContent = "Commands copied. Paste them into your terminal.";
  } catch {
    document.getElementById("copy-status").textContent = "Clipboard access unavailable. Select and copy the three commands above.";
  }
}));
