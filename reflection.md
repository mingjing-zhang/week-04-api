# Week 4 Reflection

## 1. What is the difference between the SQLAlchemy model and the Pydantic schema?

They both describe a "Book," but they live in different layers and serve different jobs.

- The **SQLAlchemy model** (`models.py::Book`) defines what the row looks like *in the database*. Each `Column(...)` maps to a real column in Postgres, with constraints like `primary_key`, `nullable`, and the SQL type (`Integer`, `String`). It is what SQLAlchemy uses to emit `SELECT`, `INSERT`, and `UPDATE` statements.
- The **Pydantic schemas** (`schemas.py::BookCreate`, `BookUpdate`, `BookResponse`) define what JSON FastAPI accepts on input and returns on output. There are three of them because the shape differs by direction: `BookCreate` has no `id` (the DB assigns it), `BookUpdate` makes everything optional (partial updates), and `BookResponse` includes `id` and turns on `from_attributes` so it can read straight off a SQLAlchemy object.

In a Java/Spring app this is similar to the split between an `@Entity` JPA class and a DTO class used by the controller.

## 2. What does `Depends(get_db)` do? Why does every endpoint need it?

`Depends(get_db)` is FastAPI's dependency injection at work. For each incoming request, FastAPI calls `get_db()`, which `yield`s a fresh SQLAlchemy `Session` bound to the request and guarantees `db.close()` runs after the response is sent (even if an exception is raised). The endpoint just receives a ready-to-use session in its `db` argument.

Every endpoint needs it because sessions are per-request. They shouldn't be shared globally — that would mix transactions from different users and leak state. `Depends(get_db)` is the boundary that makes each request its own unit of work.

## 3. When you restarted the server and your data was still there — how does that feel compared to storing data in a Python list? What changed architecturally?

In Week 3 the `books_db` list lived in the Python process. Killing `uvicorn` wiped it. The "database" was just heap memory.

In Week 4 the data lives in Postgres, which is a separate process running in its own Docker container, writing to a persistent volume (`pgdata`). FastAPI no longer *owns* the data; it just talks to the database over a TCP connection.

Architecturally, what changed is the **separation of state from compute**. The stateless app process can be killed, restarted, scaled, or replaced without losing anything. The stateful service (Postgres) stays put. This is exactly the pattern that makes real production deployments possible — you can ship new app versions every hour without worrying about user data.

## 4. What was the most confusing part of connecting the frontend to the backend?

Two things. First, internalizing that the browser hits **two separate processes** — `localhost:3000` for the Next.js page and `localhost:8000` for the API — and that the API URL has to be configurable via `NEXT_PUBLIC_API_URL` because that value gets baked into the browser bundle at build time.

Second, the Server vs Client Component distinction in the App Router. By default Next.js components render on the server, but anything using `useState`, `useEffect`, `onClick`, or `useRouter` must be marked `"use client"`. Every page in this lab needs that directive, which felt arbitrary until I understood the underlying split.

## 5. When does CORS become a problem and why? In your own words.

CORS becomes a problem the moment JavaScript on origin A (e.g. `localhost:3000`) tries to `fetch` something from origin B (e.g. `localhost:8000`). Different port = different origin. The browser blocks the response from being readable by the JS unless the server explicitly opts in with the `Access-Control-Allow-Origin` header.

The confusing part is that `curl` and Postman don't enforce CORS — only browsers do. So your API "works" from the terminal and silently breaks in the browser. The fix is one block of `CORSMiddleware` in `main.py` that adds the right headers and answers preflight OPTIONS requests. After that the browser is satisfied and `fetch` works.

## 6. What is the difference between `useEffect` with `[]` and without it?

- `useEffect(fn, [])` runs `fn` **once, after the component first mounts**. This is what you want for "fetch data on page load."
- `useEffect(fn)` (no dependency array) runs `fn` **after every render**. Since calling `setState` inside an effect triggers a re-render, this almost always creates an infinite loop. It's a footgun.
- `useEffect(fn, [x])` runs `fn` after the first render *and* every time the value of `x` changes. Useful when the effect depends on a prop or piece of state.

In the books list page I used `[]` because the fetch should happen once. In the detail page I used `[id]` so that if the route param ever changed, the new book would load.
