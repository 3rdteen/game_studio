# UNITY 6 C# REFERENCE MANUAL
- **Finding Objects:** NEVER use `FindObjectOfType()`. ALWAYS use `Object.FindFirstObjectByType<T>()`.
- **Coroutines:** If a method returns `IEnumerator`, you MUST include `using System.Collections;` at the top.
- **Input System:** If using the new Input System, you MUST include `using UnityEngine.InputSystem;`.
- **Audio:** Do not assume custom AudioControllers exist. Use standard `AudioSource` components.
- **UI:** Always use `using TMPro;` and `TextMeshProUGUI` instead of legacy Unity UI `Text`.
- NEVER invent custom random number classes like 'DiceRoller'. ALWAYS use Unity's native 'UnityEngine.Random.Range(min, max)' for any random calculations or damage rolls
- Avoid using deprecated `FindObjectOfType()` in favor of modern `Object.FindFirstObjectByType<T>()`.
- Always use `Object.FindFirstObjectByType<T>()` instead of `FindObjectOfType()` or `GetComponent<T>`, to ensure proper management of game objects. This helps in avoiding null references and ensures that the object exists before usage.
- Avoid using deprecated or legacy Unity APIs in your code, ensuring that all scripts are compatible with Unity 6 and modern C# standards.
- Always ensure that references to game objects and components are checked for null before using them to prevent null reference exceptions in Unity 6 C# scripts.
- Ensure all scripts are compatible with Unity 6 and do not use deprecated legacy APIs before submission for review.
- Always ensure that all references to GameObjects, Components, and other Unity entities are properly checked for null or invalid state before usage to avoid null reference exceptions and unintended behavior.
- Ensure all code is written specifically for Unity 6 and does not use any deprecated legacy APIs to maintain compatibility and avoid runtime errors.
Here is the new permanent rule to add to the Unity 6 development manual:

- Always ensure that all assets referenced and used in your scripts actually exist in your project's Asset Library folder. Do not use or refer to any assets that have been deleted or moved out of this directory structure, as they will cause compile errors and runtime failures.
Here is the new permanent rule for Unity 6 C# developers based on the code reviewer's rejection:

- Ensure all public members and methods have XML documentation comments to describe their purpose, parameters, return values, and any exceptions they may throw. This helps prevent future misunderstandings and misuse of the code by other developers.
- Avoid using deprecated legacy Unity APIs in all scripts to ensure compatibility with Unity 6 and follow critical coding rules.
- Avoid using deprecated legacy Unity APIs in scripts, ensuring all code is compatible with Unity 6 and modern C#.
- Ensure all scripts adhere strictly to modern C# standards compatible with Unity 6, avoiding deprecated legacy APIs at all times.
- Ensure all scripts follow Unity 6 compatibility and do not use deprecated APIs before submission for review.
- Avoid using deprecated legacy Unity APIs in all scripts to ensure compatibility with Unity 6 and prevent future rejections based on outdated code practices.
- Always use valid and active Unity APIs that are compatible with Unity 6, avoiding deprecated or legacy features to ensure code compatibility and prevent runtime issues.
Here is a new strict one-sentence rule for Unity 6 C# developers based on the rejection reason:

- Always ensure that all scripts are fully compatible with the current version of Unity 6 before submission. Do not use any deprecated or legacy APIs.
- Ensure all scripts are properly compatible with Unity 6 and avoid using deprecated or legacy APIs during development to prevent future rejections.
- Always ensure that all scripts follow Unity 6 (URP) coding standards and avoid using deprecated or legacy APIs when implementing game logic, asset management, or any other functionality related to the project.
- Ensure all scripts are using modern C# syntax and comply with Unity 6 best practices, avoiding deprecated legacy APIs to prevent compatibility issues.
- Ensure all scripts are properly tested in Unity 6 to avoid runtime errors and undefined behavior before committing them to source control.
- Always ensure that all variables used in Unity C# scripts are properly initialized before use to avoid null reference errors and other unexpected behavior, adhering strictly to Unity 6 best practices.
- Avoid using deprecated Unity APIs and ensure all scripts are compatible with Unity 6 before finalizing them for integration into the project.
- Ensure all scripts are properly anchored to the MASTER GDD and follow the defined roles strictly, avoiding any deviation or invention of assets not listed in the provided ASSET MANIFEST.
- Ensure that all code follows modern C# standards and is compatible with Unity 6, avoiding the use of deprecated or legacy APIs.
- Ensure all scripts adhere strictly to modern C# syntax and APIs compatible with Unity 6, avoiding deprecated legacy Unity APIs at all times.
- Do not use deprecated Unity APIs or write scripts that are incompatible with Unity 6, as it may cause issues in the final build and impact the game's performance. Ensure all code is modern C# specifically written for Unity 6 and follows the critical coding rules outlined in the Master GDD.
- Ensure all public properties of MonoBehaviour scripts have [SerializeField] attribute to expose them in Inspector, avoiding null references during serialization.
- Always ensure that all scripts are properly commented and follow Unity 6's coding standards, especially when using custom shaders or rendering techniques in URP to avoid confusion and maintain code readability.
- Ensure that all scripts are properly indented and follow Unity's code style guidelines to maintain readability and consistency, as poor formatting can lead to errors and make the code harder to understand and maintain.
- Always ensure that any new scripts or modifications to existing scripts comply with the current Unity 6 API and avoid using deprecated legacy Unity APIs, to maintain compatibility and prevent runtime errors in the game development process.
Here is a simple markdown bullet point containing the new permanent rule based on the Senior Code Reviewer's rejection reason:

- Always ensure that serialized fields are initialized properly in Unity 6 scripts to avoid null reference errors and unintended behavior.
- Ensure all game objects have unique, meaningful names that accurately describe their purpose or functionality to improve code readability and maintainability.
- Ensure all scripts are thoroughly tested in Unity 6 before approval to prevent functionality bugs from being shipped.
- Ensure all scripts comply with modern C# standards and are specifically written for Unity 6, avoiding deprecated legacy APIs to maintain compatibility.
- Ensure all code references valid, existing Unity 6 (URP) APIs and does not use deprecated or legacy APIs.
- Ensure all game objects and references are properly assigned before usage to prevent null reference errors and crashes.
- Ensure all variables are properly initialized and have valid values before being used to prevent unexpected behavior and potential crashes in Unity 6 C# projects.
- Ensure all C# scripts are properly tested before submission to avoid runtime errors and crashes in Unity 6 projects, adhering strictly to modern coding practices and API usage.
- Avoid hardcoding asset paths and references directly into scripts. Instead, use Unity's built-in AssetDatabase API to load assets dynamically at runtime based on their unique names or tags. This ensures better portability and avoids issues when moving assets around in your project folder structure.
- Ensure that all scripts follow Unity 6 C# coding standards and do not use deprecated or legacy APIs to maintain compatibility.
- Ensure all scripts are properly reviewed and approved before being merged into the main codebase to avoid introducing unapproved or incompatible code that does not meet project requirements for Unity 6 development.
- Always ensure that public game objects are tagged and initialized before referencing them in your scripts to avoid null reference errors and crashes.
- Avoid using deprecated Unity APIs such as `FindObjectOfType()`, legacy Input System (`Input.GetAxis` and `Input.GetButton`), custom random number classes, hardcoded camera settings, and outdated methods to ensure compatibility with Unity 6 and prevent code rejection. Always use modern Unity API for proper integration and functionality.
- Always use `Object.FindFirstObjectByType<T>()` instead of deprecated methods like `GameObject.FindGameObjectWithTag()` when retrieving game objects in Unity 6. This ensures compatibility and better performance.
- Avoid using deprecated methods and always follow the guidelines provided in the Unity 6 manual.
- Avoid using deprecated legacy APIs such as `GameObject.FindWithTag`. Use `Object.FindFirstObjectByType<T>()` instead to find objects by type for better compatibility and adherence to modern Unity practices.
- Always use `Object.FindObjectOfType<T>()` or `Object.FindTag<T>()` instead of `GameObject.FindFirstObjectByType<T>()`. Additionally, ensure to add proper null checks for any potentially uninitialized objects.
- Always initialize and check variables before using them to prevent potential runtime errors and ensure proper functionality in Unity 6 projects.
- Ensure all script interactions with game objects use modern methods like `GameObject.FindWithTag()`, `GameObject.FindObjectOfType<T>()`, or `GameObject.FindTag<T>()` to avoid deprecated API usage and potential null references.
- Avoid using deprecated methods like `GameObject.FindWithTag`. Use `Object.FindFirstObjectOfType<PlayerController>()` instead to ensure compatibility with Unity 6. Always check if objects exist before attempting to interact with them.
- Avoid using deprecated and legacy Unity API methods, such as `GameObject.FindWithTag`, `Resources.Load<T>`, and direct script references like `PlayerController` or `AudioController`. Use modern Unity API methods provided by the framework to ensure compatibility with future versions of Unity. This includes using the AssetDatabase API for loading assets dynamically and checking if objects are null before interacting with them.
- Avoid using deprecated Unity methods. Instead, use modern API methods that are documented in the Unity Manual. Always initialize variables before use to prevent null reference exceptions. Provide XML documentation comments for all public members and methods to maintain code readability and understandability.
- Use `Object.FindFirstObjectByType<T>()` instead of deprecated methods like `GameObject.FindWithTag`. This modern approach is faster and more reliable, especially when finding objects frequently during runtime.
LLM Python Error: HTTPConnectionPool(host='localhost', port=11434): Max retries exceeded with url: /api/generate (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x76b1a21696a0>: Failed to establish a new connection: [Errno 111] Connection refused'))
- Avoid making network requests to localhost on arbitrary ports in Unity C# scripts, as they can lead to connection errors and script failures.
- Do not use deprecated legacy APIs such as `GameObject.FindFirstObjectByType()` in Unity 6 C# scripts. Use the modern `Object.FindFirstObjectByType<T>()` instead.
- Avoid using deprecated or legacy Unity APIs in your scripts. Always refer to the current Unity documentation and use recommended methods provided for modern development.
- Avoid using `new GameObject()` or `GameObject.Find()` for creating game objects in scripts. Use `GameObject.FindFirstObjectByType<T>()` instead to ensure proper object management and avoid potential null references.
- Ensure that `[MenuItem]` attribute is used on standalone static methods within a class, not attached to `MonoBehaviour` classes.
- Always use `GameObject.FindWithTag` or similar methods provided by Unity to manage scene objects, rather than creating new ones with `new GameObject`, to avoid duplication and ensure proper initialization of components.
- Do not attempt to use Python or other external languages within Unity C# scripts, as it can lead to errors and compatibility issues.
- Avoid using deprecated API methods without verifying they are still supported in Unity 6. Use updated methods like `AudioSource.PlayClipAtPoint()` instead of `audioSource.PlayOneShot()`. Also, ensure that variables such as `teleportEffect` and `slideEffect`, which represent instantiated objects or prefabs, are properly defined and initialized before use to prevent null reference errors.
- Avoid using `new GameObject()` directly within the singleton class; instead, use `GameObject.FindObjectOfType<T>()` or instantiate prefabs during scene load to ensure proper instantiation of singletons.
- Avoid creating new game objects directly in scripts. Instead, use prefabs or factory methods to instantiate game objects during scene load or when required. This helps prevent duplicate objects and null reference errors. Use `GameObject.FindFirstObjectByType<T>()` for finding existing instances of a specific type or ensure that you are using prefabs properly in your project.
- Ensure that deprecated methods, such as `Input.GetAxis` in Unity 6, are replaced with their modern equivalents or properly configured old alternatives to maintain compatibility and functionality.
- Do not use deprecated methods like `GameObject.FindWithTag` or `GameObject.FindFirstObjectByType()` in Unity 6 projects. Use modern methods such as `FindObjectOfType<T>()`, `GetComponent<T>()`, or `GetComponents<T>()` instead to ensure better performance and compatibility with the latest Unity versions.
- Avoid direct creation of game objects in scripts (`new GameObject()`). Use prefabs or factory methods for instantiating objects at runtime to maintain proper object management, ensure performance, and prevent memory leaks.
- Avoid using deprecated Unity methods: Replace `Input.GetAxis` and `AudioSource.PlayClipAtPoint` with recommended alternatives such as `Input.GetKey` and `GetComponent<AudioSource>().Play()` respectively to prevent code from being flagged as non-compliant with current best practices.
- Ensure all sound effects and particles used in scripts are declared as public variables with `[SerializeField]` attribute to allow assignment in Unity Inspector, and always check that components are not null before using them.
- Always use prefabs or factory methods to instantiate objects at runtime in Unity 6 C# scripts, and avoid direct instantiation of game objects within scripts to prevent memory leaks and ensure proper object management. Use `Object.FindFirstObjectByType<T>()` for finding game objects by type instead of deprecated methods like `GameObject.FindWithTag()`.
- Avoid using deprecated Unity methods and ensure correct method usage, such as replacing `Input.GetAxisRaw` with `Input.GetKey` for improved control in handling player inputs.
- Always use `Object.FindFirstObjectByType<T>()` instead of `GameObject.FindFirstObjectByType`, ensuring consistency and avoiding deprecated methods.
- Always check for null references when accessing components to prevent runtime errors.
- Ensure all references are correctly initialized in the `Awake` method before using them to avoid `NullReferenceException`. Check if arrays or collections have elements before accessing them.
- Ensure that singleton instances are initialized correctly, avoiding potential null reference errors by checking if the instance is already set before creating a new one.
- Avoid direct instantiation of game objects in scripts. Use prefabs for all game object instances to ensure better organization, memory management, and adherence to Unity best practices.