# cheat-ui — оформление печатных шпаргалок A4

Мини-библиотека CSS для шпаргалок A4: на экране — ярко и цветасто,
на печати — светлые заливки, аккуратные рамки и читаемый текст.

## Структура проекта

```
.
├─ AGENTS.md                          правила для агентов
├─ README.md                          этот файл
├─ css/
│  └─ cheat-ui.css                    библиотека: токены, компоненты, темы, печать
├─ kit.html                           витрина компонентов и палитры
├─ examples/
│  └─ _example_cheatsheet.html        шаблон новой шпаргалки
├─ cheatsheets/
│  └─ vitest_cheatsheet.html          готовая шпаргалка, 4 листа
└─ .opencode/skills/                  локальные скилы OpenCode
```

Откройте `kit.html` в браузере, переключите тему кнопками справа снизу
или ссылкой `kit.html?theme=dark`, нажмите `Ctrl+P` — увидите печатный вид.

Git-репозиторий уже создан. Коммиты — в стиле Conventional Commits
(`feat: add vue cheatsheet`, `docs: ...`).

---

## 1. Подключение

В файле внутри `cheatsheets/` или `examples/`:

```html
<link rel="stylesheet" href="../css/cheat-ui.css">
```

В `kit.html` (лежит в корне):

```html
<link rel="stylesheet" href="css/cheat-ui.css">
```

Каркас листа:

```html
<div class="sheet">
  <div class="sheet-head accent-teal">
    <span class="sheet-number">1</span>
    <h2 class="sheet-title">Заголовок листа</h2>
  </div>

  <div class="columns">
    <section class="block accent-blue">
      <h3 class="block-title">Секция</h3>
      <pre class="code-block">…</pre>
    </section>
  </div>

  <footer class="sheet-footer">
    <span>Название · версия</span>
    <span class="page-number">1 / 4</span>
  </footer>
</div>
```

Каждый `.sheet` — отдельная страница A4. Первому листу (с обложкой)
добавьте `class="sheet sheet--cover"`.

---

## 2. Компоненты

| Класс | Что это |
| --- | --- |
| `.sheet` | лист A4 (210×297 мм) |
| `.sheet--cover` | первый лист с обложкой |
| `.cover`, `.cover__eyebrow`, `.cover__title`, `.cover__subtitle`, `.cover__meta` | шапка-обложка |
| `.sheet-head`, `.sheet-number`, `.sheet-title` | плашка заголовка листа |
| `.columns` | две колонки с разделителем |
| `.block` | секция; цвет задаётся классом `.accent-*` |
| `.block-title`, `.block-title__hint` | заголовок секции и подсказка справа |
| `.code-block` | блок кода (не рвётся между страницами) |
| `.list`, `.list--check`, `.list--tight` | списки: квадратик, галочка, плотный |
| `.callout`, `.callout__title` | выноска; модификаторы `--info/--warn/--ok/--danger` |
| `.table` | таблица с зеброй |
| `.chip`, `.chip--ok`, `.chip--bad` | «таблетки»-метки |
| `.kbd` | клавиша |
| `.grid-2`, `.grid-3` | сетки на 2 и 3 колонки |
| `.text-muted`, `.text-small` | утилиты |
| `.sheet-footer`, `.page-number` | подвал листа и номер страницы |

Подсветка кода внутри `.code-block`:

```html
<span class="tok-comment">// комментарий</span>
<span class="tok-string">'строка'</span>
<span class="tok-number">42</span>
<span class="tok-keyword">const</span>
<span class="tok-builtin">vi.fn</span>
<span class="tok-function">expect</span>
```

Полный набор примеров — в `kit.html`.

---

## 3. Акценты

Девять оттенков, у каждого три варианта: `--c` (текст и линии),
`--c-soft` (заливка), `--c-line` (рамка). Класс ставится на контейнер
и наследуется детьми.

```
.accent-red    .accent-orange .accent-amber
.accent-green  .accent-teal   .accent-cyan
.accent-blue   .accent-violet .accent-pink
```

```html
<section class="block accent-violet">…</section>
```

Внутри секции всё красится автоматически: заголовок, рамка кода,
маркеры списка, выноска по умолчанию. Выноску можно перекрасить
модификатором (`.callout--warn`) независимо от секции.

---

## 4. Темы

Тема задаётся атрибутом на `<html>`:

| Тема | Значение | Вид |
| --- | --- | --- |
| paper | без атрибута (по умолчанию) | светлая, пастельные заливки |
| vivid | `data-theme="vivid"` | максимально яркая |
| muted | `data-theme="muted"` | приглушённая, почти монохром |
| dark | `data-theme="dark"` | тёмная инверсия для экрана |

В `kit.html` тему можно передать ссылкой или переключить кнопками
(выбор запоминается в `localStorage`).

Печать всегда светлая: print-слой перебивает любую тему, от цвета
остаётся только оттенок `H`.

---

## 5. Как устроен цвет

Цвет — это оттенок `H` плюс общий рецепт насыщенности и светлоты:

```css
--h-blue: 218;

--blue:      hsl(var(--h-blue) var(--accent-s) var(--accent-l));
--blue-soft: hsl(var(--h-blue) var(--soft-s)   var(--soft-l));
--blue-line: hsl(var(--h-blue) var(--line-s)   var(--line-l));
```

- `--accent-s/l` — насыщенный цвет текста и линий;
- `--soft-s/l` — заливка (на экране пастель, на печати почти белая);
- `--line-s/l` — рамки и разделители.

Темы и печать меняют только эти переменные — поэтому пагинация не зависит
от темы, а цвета остаются согласованными. У жёлтого, циана и зелёного
светлота чуть сдвинута (`calc(... - 2…6%)`).

Изменить палитру можно только в `css/cheat-ui.css`. Агентам это запрещено.

---

## 6. Печать

- Формат A4, поля `@page { size: A4; margin: 10mm }`.
- Каждый `.sheet` начинается с новой страницы; подвал прижат к низу.
- Заголовки, код, выноски, таблицы и пункты списков не разрываются
  между страницами; выноска остаётся при своём коде.
- **В диалоге печати включите «Фон и изображения»** (Background graphics).
- Номер страницы в подвале — обычный текст (`1 / 4`), обновляется вручную:
  Chrome в headless-печати не считает `counter(page)`.

Ручная проверка после создания шпаргалки:

```sh
python .opencode/skills/cheat-ui-print-audit/scripts/check_print.py \
  cheatsheets/vue_cheatsheet.html /tmp/vue.pdf
```

Добавьте `--theme dark`, чтобы убедиться: тёмная тема печатается светлой
и даёт то же число страниц. Подробности — в скиле `cheat-ui-print-audit`.

---

## 7. Новая шпаргалка

Имя файла: `<subject>_cheatsheet.html`, латиница, нижний регистр,
например `vue_cheatsheet.html`. Файл кладётся в `cheatsheets/`.

Агент обязан сначала задать вопросы и дождаться ответов:

1. предмет и имя файла;
2. уровень — `начальный / средний / hard / всё` («всё» = все блоки,
   пользователь сам удаляет лишнее);
3. стек, версия и язык примеров;
4. объём — 2 / 3 / 4 листа или «как упакуется»;
5. конкретные блоки и их объём из меню:

| Блок | Объём |
| --- | --- |
| Установка и запуск | 5–8 строк команд |
| Каркас / базовый синтаксис | 8–12 строк |
| Основные API и методы | 6–10 пунктов |
| Таблица сравнений | 3–5 строк |
| Готовые рецепты | 2–4 сниппета по 6–10 строк |
| Конфигурация | 6–10 строк |
| Ошибки и подводные камни | 4–6 пунктов |
| Продвинутые возможности (middle/hard) | 2–4 блока |
| Тестирование и отладка | 5–8 строк |

Полный сценарий — в `.opencode/skills/cheat-ui/references/questionnaire.md`.

Совет: один лист = одна тема. Так проще найти нужное на бумаге и не ломать
пагинацию при правках.

---

## 8. Для агентов

- `AGENTS.md` — жёсткие правила: только создание новых шпаргалок, обязательный
  опрос, запрет на стили и существующие файлы, Conventional Commits.
- `.opencode/skills/cheat-ui/SKILL.md` — скил на опрос и создание шпаргалки.
- `.opencode/skills/cheat-ui-print-audit/SKILL.md` — скил на ручную проверку
  печати; скрипт `scripts/check_print.py` рендерит PDF и печатает отчёт.

Скилы подхватываются OpenCode автоматически из `.opencode/skills/`.
Коммиты делает пользователь; агент лишь предлагает сообщение.
