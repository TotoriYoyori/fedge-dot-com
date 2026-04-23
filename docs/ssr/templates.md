# Template Files and Convention 🎨

FEDGE uses Jinja2 for templating. We follow a modular approach where templates can reside either globally or within specific domain modules.

---

## 1. Template Discovery System 🔍

The core logic in `src/templates.py` automatically discovers template directories. It looks for folders named `templates/` in:
1.  The base `src/` directory.
2.  Any immediate subdirectory of `src/` (domain modules).

```python
# src/templates.py
def _discover_dirs(folder_name: str) -> list[str]:
    dirs = []
    # Check src/templates
    # Check src/*/templates
    ...
    return dirs

page_loader = FileSystemLoader(_discover_dirs("templates"))
templates = Jinja2Templates(env=Environment(loader=page_loader))
```

This means you can simply create a `templates/` folder in your new module, and FEDGE will find it!

---

## 2. File Naming and Organization 📂

- **Global Templates**: Base layouts, common components (nav, footer), and shared macros live in `src/templates/`.
- **Domain Templates**: Module-specific pages (e.g., `login.html`, `dashboard.html`) live in `src/<domain>/templates/`.

### Convention
Use **snake_case** for template filenames.
- `base.html`
- `auth_base.html`
- `user_profile.html`

---

## 3. Inheritance Pattern 🧬

We use a multi-level inheritance pattern to keep templates DRY (Don't Repeat Yourself).

1.  **Level 1: `base.html`**: The root layout (HTML structure, global CSS/JS).
2.  **Level 2: `domain_base.html`**: (Optional) Domain-specific layout (e.g., `auth_base.html` adding auth-specific styles or headers).
3.  **Level 3: `page.html`**: The actual content page (e.g., `login.html`).

---

## 4. Jinja2 Best Practices 💡

### Use `url_for` for internal links
Never hardcode URLs in templates. Use the `request.url_for` helper:
```html
<!-- INCORRECT -->
<a href="/login">Login</a>

<!-- CORRECT -->
<a href="{{ request.url_for('login_page') }}">Login</a>
```

### Passing Data to Templates
Data is passed via the `context` dictionary in `TemplateResponse`:
```python
return templates.TemplateResponse(
    request=request,
    name="profile.html",
    context={"user": user, "stats": user_stats}
)
```
In Jinja2: `Welcome, {{ user.username }}!`
