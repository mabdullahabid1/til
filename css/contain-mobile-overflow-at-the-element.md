# Contain Mobile Overflow at the Element

Wide tables and code blocks should own their horizontal scrolling. Hiding overflow on the page can mask the symptom while a child element still widens the mobile layout.

Constrain the wide element and give it a local scroll boundary:

```css
.content table,
.content pre {
  display: block;
  max-width: 100%;
  overflow-x: auto;
}
```

Test at the target viewport and compare `document.documentElement.scrollWidth` with `window.innerWidth`. They should match, while the table or code block remains horizontally scrollable.

Source: [abd.dev PR #22](https://github.com/mabdullahabid/abd.dev/pull/22)
