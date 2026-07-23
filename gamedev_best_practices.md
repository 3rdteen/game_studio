# THE AI STUDIO GAME DESIGN & ARCHITECTURE BIBLE
**Core Philosophy:** Based on the principles of "Unity in Action", "Game Programming Algorithms and Techniques", classic engine architecture, and modern Unity 6 standards. 

## 1. Architecture & Decoupling (The "No God-Class" Rule)
* **Component-Based Design:** Scripts must do ONE thing perfectly (Single Responsibility Principle). Break large scripts into `PlayerMovement.cs`, `PlayerHealth.cs`, and `WeaponController.cs`.
* **Centralized Input Management:** NEVER scatter `Input.GetKey` or `Input.GetButton` across dozens of scripts. Create a single `InputManager` or use the new Unity Input System to read inputs, and have gameplay scripts listen to those input events.
* **Never Cross-Wire UI and Gameplay:** Gameplay scripts MUST NEVER directly manipulate UI text or images. The UI should *listen* to the game state via Events/Delegates.

## 2. Managers & State Machines
* **The GameManager:** Maintain a single centralized `GameManager` to handle high-level game states (MainMenu, Playing, Paused, GameOver). 
* **State Machines for AI:** Enemy AI must not use massive `if/else` blocks in the `Update()` loop. Implement Finite State Machines (FSM) using enums (e.g., `enum State { Patrol, Chase, Attack }`).

## 3. The Game Loop & Time Management (CRITICAL)
* **Frame Rate Independence:** Any code that moves, rotates, or scales an object continuously MUST be multiplied by `Time.deltaTime`. 
* **The Update vs. FixedUpdate Split:** 
  * Physics calculations (adding forces, modifying Rigidbody velocity) MUST go in `FixedUpdate()`. 
  * Visuals, timers, and input detection MUST go in `Update()`. 
  * NEVER check for one-frame inputs (like `Input.GetKeyDown`) inside `FixedUpdate()`.
* **Camera & UI Rendering:** Use `LateUpdate()` strictly for Camera following and UI tracking to prevent screen jitter.

## 4. Performance, Memory, & Collisions
* **Primitive Colliders Only:** Avoid using `MeshCollider` for moving objects. Rely strictly on Box, Sphere, and Capsule colliders. Complex collisions waste CPU cycles and lower frame rates.
* **Never Search in Update:** NEVER use `Object.FindFirstObjectByType<T>()`, `GameObject.Find()`, or `GetComponent<T>()` inside `Update()`. Cache these references inside `Awake()` or `Start()`.
* **Object Pooling:** If the game involves shooting bullets or spawning enemies, DO NOT use `Instantiate()` and `Destroy()` during gameplay. Create an Object Pool and reuse inactive GameObjects to prevent Garbage Collection stutters.

## 5. Game Feel & "Juice" (The Player Experience)
* **Telegraphing:** Enemies must visually or audibly "wind up" or telegraph their attacks at least 0.5 seconds before dealing damage.
* **Impact Feedback:** Every successful hit, jump, or point scored must have immediate feedback (particle effects, audio clips, or camera shake). 
* **Immediate Readability:** Ensure silhouettes and colors clearly visually separate the Player, Enemies, and Background.
