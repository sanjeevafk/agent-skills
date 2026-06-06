# Type Techniques Reference

Deep examples for the five core TypeScript type manipulation techniques.

## Table of Contents
1. [Conditional Types](#conditional-types)
2. [Mapped Types](#mapped-types)
3. [Key Remapping in Mapped Types](#key-remapping)
4. [The `infer` Keyword](#infer)
5. [Template Literal Types](#template-literal-types)
6. [Combining Techniques](#combining-techniques)

---

## Conditional Types

Conditional types let a type resolve differently depending on whether a type constraint is satisfied. The syntax mirrors JavaScript's ternary operator.

```typescript
type IsString<T> = T extends string ? true : false;
```

**Real-world example — API response typing:**

```typescript
// A response type that branches on whether the request succeeded
type ApiResponse<T> = T extends { success: true }
  ? { data: T }
  : { error: string };

// Usage
type SuccessPayload = { success: true; userId: number };
type OkResponse = ApiResponse<SuccessPayload>;
// OkResponse = { data: { success: true; userId: number } }

type FailPayload = { success: false };
type ErrResponse = ApiResponse<FailPayload>;
// ErrResponse = { error: string }
```

**Distributing over unions:**
When you apply a conditional type to a union, TypeScript distributes it over each member automatically:

```typescript
type ToArray<T> = T extends any ? T[] : never;
type StrOrNumArrays = ToArray<string | number>;
// Result: string[] | number[]   (not (string | number)[])
```

**Filtering with `never`:**
```typescript
// Extract only function-typed properties from a type
type FunctionKeys<T> = {
  [K in keyof T]: T[K] extends Function ? K : never;
}[keyof T];

interface Foo { bar(): void; baz: string; qux(): number }
type FooFns = FunctionKeys<Foo>; // 'bar' | 'qux'
```

---

## Mapped Types

Mapped types iterate over the keys of an existing type and produce a new type by transforming each key-value pair.

```typescript
// Make all properties optional
type Partial<T> = {
  [P in keyof T]?: T[P];
};

// Make all properties required
type Required<T> = {
  [P in keyof T]-?: T[P]; // The `-?` removes optionality
};

// Make all properties readonly
type Readonly<T> = {
  readonly [P in keyof T]: T[P];
};
```

**Real-world example — nullable variant:**

```typescript
interface User {
  name: string;
  age: number;
  email: string;
}

// All properties become T | null — useful for database result rows
type Nullable<T> = {
  [P in keyof T]: T[P] | null;
};

type NullableUser = Nullable<User>;
// { name: string | null; age: number | null; email: string | null }
```

**Filtering properties by value type:**
```typescript
// Keep only properties whose value extends a given type
type PickByValue<T, V> = {
  [K in keyof T as T[K] extends V ? K : never]: T[K];
};

interface Form {
  username: string;
  age: number;
  isAdmin: boolean;
  email: string;
}

type StringFields = PickByValue<Form, string>;
// { username: string; email: string }
```

---

## Key Remapping

Key remapping (introduced in TypeScript 4.1) lets you transform the *names* of keys during a mapped type, using an `as` clause.

```typescript
type Prefixed<T, Prefix extends string> = {
  [K in keyof T as `${Prefix}${string & K}`]: T[K];
};

interface User { name: string; age: number }
type PrefixedUser = Prefixed<User, 'user_'>;
// { user_name: string; user_age: number }
```

**Real-world example — getter/setter pairs:**

```typescript
// Generate getter methods for every property in a type
type Getters<T> = {
  [K in keyof T as `get${Capitalize<string & K>}`]: () => T[K];
};

interface Person { name: string; age: number }
type PersonGetters = Getters<Person>;
// { getName: () => string; getAge: () => number }
```

**Filtering keys with remapping:**
```typescript
// Exclude keys starting with underscore (convention: private-ish)
type PublicOnly<T> = {
  [K in keyof T as K extends `_${string}` ? never : K]: T[K];
};
```

---

## The `infer` Keyword

`infer` appears inside conditional types to *capture* a type that TypeScript infers from a structural match. Think of it like pattern matching on types.

```typescript
// Built-in ReturnType, reimplemented:
type ReturnType<T> = T extends (...args: any[]) => infer R ? R : never;

type Fn = () => { userId: number; name: string };
type Result = ReturnType<Fn>; // { userId: number; name: string }
```

**Extracting array element type:**
```typescript
type ElementType<T> = T extends (infer E)[] ? E : never;

type Strs = ElementType<string[]>; // string
type Nums = ElementType<number[]>; // number
```

**Extracting promise value:**
```typescript
type Awaited<T> = T extends Promise<infer V> ? V : T;

type Resolved = Awaited<Promise<string>>; // string
type Plain = Awaited<number>;             // number
```

**Extracting constructor parameter types:**
```typescript
type ConstructorParams<T> = T extends new (...args: infer P) => any ? P : never;

class Connection { constructor(host: string, port: number) {} }
type Params = ConstructorParams<typeof Connection>; // [host: string, port: number]
```

**Real-world example — inferring middleware context:**
```typescript
// Given a middleware function, extract the context type it injects
type MiddlewareCtx<T> = T extends (ctx: infer C, next: () => void) => void ? C : never;

type MyMiddleware = (ctx: { user: { id: string } }, next: () => void) => void;
type Ctx = MiddlewareCtx<MyMiddleware>; // { user: { id: string } }
```

---

## Template Literal Types

Template literal types let you express string patterns at the type level. They compose with unions to enumerate all combinations.

```typescript
type HttpMethod = 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';
type ApiRoute = 'users' | 'posts' | 'comments';

type Endpoint = `${HttpMethod} /api/${ApiRoute}`;
// 'GET /api/users' | 'GET /api/posts' | 'GET /api/comments'
// | 'POST /api/users' | ... (20 combinations total)
```

**Real-world example — event system typing:**
```typescript
type EventName<Entity extends string, Action extends string> = `${Entity}:${Action}`;

type UserEvents = EventName<'user', 'created' | 'updated' | 'deleted'>;
// 'user:created' | 'user:updated' | 'user:deleted'

// Combined with a mapped type for a fully typed event bus:
type EventHandlers<Events extends string> = {
  [E in Events]: (payload: unknown) => void;
};
```

**CSS class pattern enforcement:**
```typescript
type ColorScale = 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9;
type TailwindColor = 'slate' | 'blue' | 'green' | 'red';
type TailwindBg = `bg-${TailwindColor}-${ColorScale}00`;
// 'bg-slate-100' | 'bg-slate-200' | ... | 'bg-red-900'
```

**SQL query builder patterns:**
```typescript
type Column<Table extends string, Col extends string> = `${Table}.${Col}`;
type UserCols = Column<'users', 'id' | 'name' | 'email'>;
// 'users.id' | 'users.name' | 'users.email'
```

---

## Combining Techniques

The real power of TypeScript's type system emerges when you compose these features together.

**Example — deep readonly:**
```typescript
// Recursively make all nested properties readonly
type DeepReadonly<T> = T extends (infer E)[]
  ? ReadonlyArray<DeepReadonly<E>>
  : T extends object
  ? { readonly [K in keyof T]: DeepReadonly<T[K]> }
  : T;
```
This uses `infer` to handle arrays, conditional types to branch on object vs. primitive, and a mapped type to apply `readonly` at every level.

**Example — typed event emitter:**
```typescript
type EventMap = {
  'user:login': { userId: string; timestamp: number };
  'user:logout': { userId: string };
  'post:created': { postId: string; authorId: string };
};

type Listener<Map, E extends keyof Map> = (payload: Map[E]) => void;

class TypedEmitter<Map> {
  on<E extends keyof Map>(event: E, listener: Listener<Map, E>): void {
    // ...
  }
  emit<E extends keyof Map>(event: E, payload: Map[E]): void {
    // ...
  }
}

const emitter = new TypedEmitter<EventMap>();
emitter.on('user:login', ({ userId, timestamp }) => {
  // userId: string, timestamp: number — fully inferred ✓
});
```

**Example — form validation schema derived from interface:**
```typescript
type ValidationRule<T> = T extends string
  ? { minLength?: number; maxLength?: number; pattern?: RegExp }
  : T extends number
  ? { min?: number; max?: number }
  : T extends boolean
  ? { required?: boolean }
  : never;

type FormSchema<T> = {
  [K in keyof T]: ValidationRule<T[K]>;
};

interface SignupForm { username: string; age: number; agreeToTerms: boolean }
type SignupSchema = FormSchema<SignupForm>;
// {
//   username: { minLength?: number; maxLength?: number; pattern?: RegExp };
//   age: { min?: number; max?: number };
//   agreeToTerms: { required?: boolean };
// }
```
