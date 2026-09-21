**`fol_symbols`**

$$
\forall  x_{0}:\mathrm{service}, ((\mathrm{deployed}(x_{0})) \to  (\exists  x_{1}:\mathrm{person}, (\mathrm{owns}(x_{1}, x_{0})))).
$$

**`fol_keywords`**

```text
forall x0:service, ((deployed(x0)) implies (exists x1:person, (owns(x1, x0)))).
```

**`ve_strict`**

```text
for every service x0, (if (x0 is deployed), then (there exists person x1, (x1
owns x0))).
```

**`ve_natural`**

```text
for every service x0: (if (x0 is deployed), then (there is a person x1 such that
(x1 owns x0))).
```

**`ve_fluent`**

```text
for every service S that is deployed, there is a person P such that P owns S.
```

<!-- src: paper/sources/worked-example.env.json; paper/sources/worked-example.ve; ve/printer.py; ve/fluent.py. Exact strings and AST: paper/generated/worked-example.json. -->
