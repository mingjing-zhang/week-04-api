# Week 4 Reflection

Context for these answers: my background is Java EE — Spring + Hibernate, single WAR deployed into Tomcat, JSP rendering on the server. This week is the first time I've put together a modern stack (Next.js + FastAPI + Postgres) end-to-end, and I want to use this reflection to capture both the technical lessons and the architectural shift I'm feeling.

## 1. What is the difference between the SQLAlchemy model and the Pydantic schema?

They both describe a "Book," but they live in different layers.

- The **SQLAlchemy model** (`models.py::Book`) describes what the row looks like *in the database*. Each `Column(...)` maps to a real Postgres column with constraints like `primary_key`, `nullable`, and type. SQLAlchemy uses it to emit `SELECT`, `INSERT`, `UPDATE`.
- The **Pydantic schemas** (`schemas.py`) describe what JSON FastAPI accepts on input and returns on output. There are three of them because the shape differs by direction: `BookCreate` has no `id` (the DB assigns it), `BookUpdate` makes everything optional (partial updates), and `BookResponse` includes `id` and turns on `from_attributes` so it can read straight off a SQLAlchemy object.

Coming from Java, this is the same separation as a JPA `@Entity` versus a DTO returned from a `@RestController`. The mistake I want to avoid is treating them as the same object — they look similar but they belong to different layers and should be allowed to drift independently. I learned the hard way in Hibernate that object-relational impedance mismatch is a real thing (lazy loading, N+1, dirty session); Pydantic + SQLAlchemy reproduces a lighter-weight version of that split.

## 2. What does `Depends(get_db)` do? Why does every endpoint need it?

`Depends(get_db)` is FastAPI's dependency injection. For each incoming request, FastAPI calls `get_db()`, which `yield`s a fresh SQLAlchemy `Session` and guarantees `db.close()` runs after the response is sent — even if the endpoint raised. The endpoint just receives a ready-to-use session as a parameter.

Every endpoint needs it because sessions are per-request. Sharing a session globally would mix transactions from different users and leak state.

The Java parallel is Spring's `@Autowired` + `@Transactional`. Spring's DI is heavier (annotation scanning, application context, bean lifecycle). FastAPI's `Depends()` is a much lighter version of the same idea — just a function that yields a resource — but the principle of "give the handler what it needs, framework manages the lifecycle" is identical.

## 3. When you restarted the server and your data was still there — how does that feel compared to storing data in a Python list? What changed architecturally?

In Week 3 the `books_db` list lived in the Python process. Killing `uvicorn` wiped it. The "database" was just heap memory of one process.

In Week 4 the data lives in Postgres, which is a separate process in its own Docker container, writing to a persistent volume (`pgdata`). FastAPI no longer *owns* the data — it just talks to the database over a TCP connection.

What changed architecturally is the **separation of state from compute**. The stateless app process can be killed, restarted, or replaced without losing anything; the stateful service stays put. This is the foundation of everything modern in deployment — rolling restarts, blue/green, horizontal scaling all depend on this split.

The bigger meta-shift I felt this week is from the Java EE monolith mindset ("one big process owns everything") to "small specialized services talk over the network." In my Java days the network was implicit and almost invisible — methods calls inside the same JVM. Now the network is a first-class architectural concern: the browser talks to two ports, the backend talks to the database over TCP, every boundary is HTTP or SQL. The complexity moves from "managing object lifecycles inside one process" to "making sure independent processes can find each other and stay in sync."

## 4. What was the most confusing part of connecting the frontend to the backend?

Two things.

First, internalizing that the browser is hitting **two separate processes** — `localhost:3000` for the Next.js page and `localhost:8000` for the API. Coming from a JSP world where the server returned a fully-rendered page, it took me one screw-up (I hit `localhost:8000/books` in the address bar and got raw JSON) to really feel the split. After that mistake the whole architecture clicked.

Second, the Server vs Client Component distinction. By default Next.js components render on the server, but anything using `useState`, `useEffect`, `onClick`, or `useRouter` must be marked `"use client"`. The mind-shift is that in one component tree, different components can run in different environments and the framework wires them together. This doesn't have a clean Java analogy — JSF and Vaadin come close but never let a single tree mix server-rendered and client-interactive nodes the way RSC does.

A meta-observation about this transition: I noticed that almost all my Spring/Hibernate operational knowledge (XML config, session management, Maven idioms) had to be set aside this week. The way to write a server now is genuinely different — async event loop instead of one-thread-per-request, type hints + Pydantic instead of compile-time JavaBeans. That said, the higher-level intuitions I picked up in Java — where transaction boundaries should sit, where N+1 queries hide, when to worry about connection pool exhaustion — transferred directly. The vocabulary changed; the architectural questions didn't.

## 5. When does CORS become a problem and why? In your own words.

CORS becomes a problem the moment JavaScript on origin A (e.g. `localhost:3000`) tries to `fetch` from origin B (e.g. `localhost:8000`). Different port = different origin in the browser's view. The browser blocks the response from being readable by the page's JS unless the server explicitly opts in by sending `Access-Control-Allow-Origin`.

The reason this didn't exist in the Java/JSP era is that **the JSP page was rendered on the same origin that served the API call**. There was no cross-origin issue because there was no separation. Now that the frontend has been promoted from "view layer of the backend" to "an independent application running in the browser," the browser's same-origin-policy kicks in and CORS is the agreed-upon way to safely opt out of it.

The confusing detail is that `curl` and Postman don't enforce CORS — only browsers do. So your API "works fine" from the terminal and silently breaks in the browser. The fix is a one-block `CORSMiddleware` in `main.py` — conceptually identical to a Spring `CorsFilter` or Tomcat's built-in `CorsFilter`.

## 6. What is the difference between `useEffect` with `[]` and without it?

- `useEffect(fn, [])` runs `fn` **once, after the component first mounts**. This is what I used in the books list page — fetch the data once when the page opens.
- `useEffect(fn)` (no array) runs `fn` **after every render**. Since calling `setState` inside an effect triggers a re-render, this almost always creates an infinite loop. It's a footgun the framework gives you for completeness.
- `useEffect(fn, [x])` runs `fn` after the first render *and* every time `x` changes. I used this in the detail page with `[id]` so the right book reloads if the route param changes.

The deeper mental shift here, coming from imperative jQuery/DOM-manipulation thinking, is that React is **declarative**. I describe what the UI looks like for a given state, and React figures out the DOM updates. `useEffect` is the controlled escape hatch for things that happen *outside* the declarative model — network calls, timers, subscriptions. The dependency array is how I tell React which state changes should re-trigger that escape hatch.

---

## Closing thought

Three observations I want to capture for future me:

1. **The frontend UX gap is real.** What I built this week — three pages with smooth client-side navigation, no full-page reloads, decent default styling from Tailwind — would have taken weeks of hand-written JavaScript and CSS in the JSP era. Twenty years of compound progress in frontend tooling is sitting under the surface of this stack.

2. **Python on the backend matters for the AI half of my work.** All the model SDKs, training libraries, and AI tooling live in Python. Having backend and AI workloads share one language, one package manager, and one mental model removes a real cognitive cost that I'd hit if the backend were Java.

3. **AI assistants are very strong on this exact stack.** Next.js + FastAPI + Postgres is the most-documented combination in recent training data, so Claude (and others) generate it fluently. The flip side is the "mainstream bias" — when I work on this stack with AI, I should let it accelerate execution but keep architectural judgment (data modeling, where to draw the front/back boundary, where async helps and where it doesn't) firmly in my own hands.
