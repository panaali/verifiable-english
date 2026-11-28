// Inventory literal text in the shipped browser code. Acorn is provided by Node.
const fs = require('fs');
const acorn = require('acorn');
const source = fs.readFileSync(process.argv[2], 'utf8');
const tree = acorn.parse(source, {ecmaVersion: 'latest', locations: true});
const literals = new Set();
function visit(node) {
  if (!node || typeof node !== 'object') return;
  if (node.type === 'Literal' && typeof node.value === 'string') literals.add(node.value);
  if (node.type === 'TemplateLiteral') {
    literals.add(node.quasis.map(part => part.value.cooked).join('{}'));
  }
  for (const value of Object.values(node)) {
    if (Array.isArray(value)) value.forEach(visit);
    else if (value && typeof value === 'object') visit(value);
  }
}
visit(tree);
process.stdout.write(JSON.stringify([...literals].sort()));
