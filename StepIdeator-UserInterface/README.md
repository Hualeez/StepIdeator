# StepIdeator-UserInterface

The frontend for StepIdeator

### Key Dependencies

- `Node.js`: Run `node -v` to check if `Node.js` is installed. The development environment uses Node.js version v16.16.0, but the application also runs successfully on version v18.18.2.
- `react-sketch-canvas`: An open-source drawing library used for implementing drawing functionality. While there may be some bugs in this implementation, no issues have been encountered during use so far. Ongoing updates and feature enhancements of this library should be monitored. More information can be found here: https://github.com/vinothpandian/react-sketch-canvas .
- `tailwindcss`: A commonly used CSS framework for styling.
- `next.js`: The project is developed using Next.js version 13 with the latest App Router mode. Documentation can be found at: https://nextjs.org/docs/app .

### Project Architecture

The project architecture is as follows:

``` sh
├── LICENSE
├── next.config.js
├── next-env.d.ts
├── package.json
├── package-lock.json
├── postcss.config.js
├── public
│   ├── audios
│   ├── fonts
│   ├── icons
│   └── images
├── README.md
├── src
│   ├── app
│   ├── components
│   ├── configs
│   ├── lib
│   ├── mocks
│   ├── services
│   ├── styles
│   ├── theme
│   └── types.d.ts
├── tailwind.config.ts
├── tsconfig.json
├── typings.d.ts
└── yarn.lock
```

The configuration files are located in the `./src/configs` directory and include the following:
- `env.ts`: API service configuration.
- `routes.ts`: Page routing configuration. When adding a new page, you first need to create the corresponding page file in the `app` folder. Then, configure the page name and other details in `routes.ts` to enable navigation. Without this configuration, the new page won’t be accessible through navigation.
- `site.ts`: Site information configuration. This file is used to configure site-related details such as the website name, logo, and description.


## Quick start

1. Start the API service before running the project, start the 'StepIdeator-API' service. The API URL configuration can be found in `./src/configs/env.ts`.
2. Run the following command to install the project dependencies (stored in node_modules):
    ```bash
    npm install
    ```
    or use Yarn:
    ```bash
    yarn install
    ```
3. Start the development server on the default port (3000) by running:
    ```bash
    npm run dev
    ```
    or use Yarn:
    ```bash
    yarn dev
    ```
    
You can access the frontend at http://localhost:port in your browser.

