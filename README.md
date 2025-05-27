![SocialBanner](https://github.com/user-attachments/assets/ca667a8a-068a-4045-b40b-5143cf29b10f)
# 

Welcome to **IVYSTUDY**, a dynamic and interactive study platform designed to provide free access to lessons and study materials. This documentation explains the structure and functionality of IVYSTUDY.

---
## Navigation Links

| #  | Hyperlink                     | Description                                                                 |
|----|-----------------------------|-----------------------------------------------------------------------------|
| 1  | [Search](www.ivystudy.org)       | The main resource page/search feature         |
| 1  | [Statistics](www.ivystudy.org/info)       | The statistics page         |
| 2  | [Page Backups and HTML](https://github.com/NagusameCS/Backups/tree/main)       | The Repo were the HTML for the page will be stored and backed up         |



## Table of Contents

| #  | Section                     | Description                                                                 |
|----|-----------------------------|-----------------------------------------------------------------------------|
| 1  | [Overview](#overview)       | Introduction to IVYSTUDY's structure, goals, and design principles.         |
| 2  | [Features](#features)       | Highlights of responsive design, dark mode, search, and interactivity.      |
| 3  | [File Structure](#file-structure) | Overview of the single-file layout and reliance on external libraries.      |
| 4  | [HTML Structure](#html-structure) | Breakdown of `<head>` and `<body>` elements and their roles.               |
| 5  | [CSS Styling](#css-styling) | Description of theming, responsiveness, animations, and dark mode styling. |
| 6  | [JavaScript Functionality](#javascript-functionality) | Handles dynamic loading, modal display, search, and dark mode toggle.       |
| 7  | [Meta Tags and SEO](#meta-tags-and-seo) | Details Open Graph tags for better social sharing and SEO visibility.      |
| 8  | [Dark Mode](#dark-mode)     | Explanation of how dark mode is implemented and stored using localStorage.  |
| 9  | [Dynamic Content Loading](#dynamic-content-loading) | Lessons are fetched and rendered based on filters and search.              |
| 10 | [Search Functionality](#search-functionality) | Real-time suggestions, filtering, and term highlighting.                   |
| 11 | [Lesson Modal](#lesson-modal) | Displays lessons with Markdown + LaTeX support and navigation controls.    |
| 12 | [Social Banner](#social-banner) | Banner image appears when the site is shared via social media platforms.   |
| 13 | [License](#license)         | Licensing terms for using and distributing the project.                     |

---

## Overview

The IVYSTUDY platform is built on a single html file. It includes a responsive design, dynamic content loading, and interactive features to enhance the user experience. The file integrates various libraries and frameworks to provide a seamless and modern interface.

---

## Features

- **Responsive Design**: Optimized for all screen sizes using Tailwind CSS.
- **Dark Mode**: Toggle between light and dark themes.
- **Dynamic Content Loading**: Fetches lessons and resources from a remote repository.
- **Search Functionality**: Real-time search with suggestions and filtering.
- **Lesson Modal**: Displays lesson content in a modal with support for Markdown and LaTeX.
- **Social Banner**: Automatically displays a banner when the page is shared.
- **Interactive Elements**: Includes animations, dropdowns, and hover effects.

---

## File Structure

The `index.html` file is self-contained and relies on external libraries for styling and functionality.

---

## HTML Structure

### Head Section

The `<head>` section includes:

1. **Meta Tags**:
   - `viewport`: Ensures responsive design.
   - `og:title`, `og:description`, `og:image`, `og:url`, `og:type`: Open Graph tags for social sharing.

2. **External Libraries**:
   - Tailwind CSS for styling.
   - Google Fonts for typography.
   - Highlight.js for syntax highlighting.
   - KaTeX for rendering LaTeX equations.
   - Markdown-it and plugins for Markdown rendering.

3. **Custom Styles**:
   - Defined using CSS variables for easy theming.
   - Includes animations, hover effects, and dark mode styles.

### Body Section

The `<body>` section is divided into the following components:

1. **Loading Screen**:
   - Displays a loading animation while the page initializes.

2. **Hero Section**:
   - Contains the platform title and a brief description.

3. **Search Bar**:
   - Allows users to search for lessons, topics, or subjects.
   - Includes real-time suggestions and results.

4. **Class Filter**:
   - Displays subject pills for filtering lessons by category.

5. **Content Section**:
   - Dynamically loads lessons and resources based on filters and search queries.

6. **Lesson Modal**:
   - A modal for displaying lesson content with Markdown and LaTeX support.

7. **Footer**:
   - Links to Terms, Privacy, and Contact pages.

8. **Dark Mode Toggle**:
   - A floating button to switch between light and dark themes.

---

## CSS Styling

### Key Features

1. **Custom Variables**:
   - `--primary`: Primary color for text and accents.
   - `--accent`: Secondary color for backgrounds and highlights.

2. **Animations**:
   - `fadeIn`: Smooth fade-in effect.
   - `spin`: Loading spinner animation.

3. **Dark Mode**:
   - Overrides light mode styles with darker colors for better readability.

4. **Responsive Design**:
   - Uses Tailwind CSS classes for mobile-first design.

---

## Advanced CSS Styling

### Enhanced Markdown Styling

The platform includes custom styles for rendering Markdown content beautifully:

1. **Headings**:
   - `h1`, `h2`, `h3`: Styled with bold fonts, custom colors, and spacing for
   - Common Github MD Syntax
     
2. **Paragraphs**:
   - Line height and spacing are optimized for readability.
   - Common Github MD Syntax
     
3. **Blockquotes**:
   - Styled with a left border and background color for emphasis.
   - Common Github MD Syntax
     
4. **Lists**:
   - Custom bullet and number styles with proper indentation.
   - Common Github MD Syntax
     
5. **Code Blocks**:
   - Syntax highlighting using Highlight.js.
   - Styled with a light background, rounded corners, and padding.
   - Common Github MD Syntax
     
6. **Tables**:
   - Borders, padding, and alternating row colors for better visibility.
   - Common Github MD Syntax
     
7. **Images**:
   - Responsive with rounded corners and spacing.
   - Common Github MD Syntax

8. **Markschemes**:
   - Done via the following syntax

   ```MD
   <details>
   <summary>Markscheme</summary>
   
   CONTENT IN HERE
   
   </details>
   ```
   
9. LaTeX Adjacent MD Math
    - Done via the following syntax

   ```MD
   (Normal)
   $$
   Content
   $$
   
   (For Inline)
   $$ Content $$
   ```
---

## JavaScript Functionality

### Key Features

1. **Dynamic Content Loading**:
   - Fetches curriculum data from a remote JSON file.
   - Processes and displays lessons based on filters and search queries.

2. **Search Functionality**:
   - Real-time search with debounce to improve performance.
   - Highlights matching terms in results.

3. **Lesson Modal**:
   - Fetches and renders lesson content in Markdown format.
   - Supports LaTeX rendering using KaTeX.

4. **Dark Mode**:
   - Toggles between light and dark themes.
   - Saves user preference in `localStorage`.

5. **Social Banner**:
   - Displays a banner image when the page is shared on social media.

---

## JavaScript Functionality (Detailed)

### Dynamic Content Loading

The platform dynamically fetches and renders lessons from a remote JSON file. The process involves:

1. **Fetching Data**:
   - Uses the `fetch` API to retrieve lesson data.

2. **Processing Data**:
   - Parses the JSON response and flattens it into a list of lessons.

3. **Rendering Content**:
   - Filters lessons based on user input and displays them dynamically.

### Search Functionality

The search bar provides real-time suggestions and results:

1. **Debounce Mechanism**:
   - Prevents excessive API calls by delaying the search execution.

2. **Highlighting Matches**:
   - Highlights matching terms in the search results for better visibility.

3. **Filtering**:
   - Filters lessons based on the search query and selected categories.

### Lesson Modal

The lesson modal displays detailed content for each lesson:

1. **Markdown Rendering**:
   - Converts Markdown to HTML using Markdown-it.
   - Supports GitHub Flavored Markdown (GFM) features.

2. **LaTeX Rendering**:
   - Renders mathematical equations using KaTeX.

3. **Navigation**:
   - Includes "Previous" and "Next" buttons for navigating between lessons.

### Dark Mode

Dark mode is implemented using a combination of CSS and JavaScript:

1. **CSS**:
   - Defines dark mode styles using the `.dark-mode` class.
   - Overrides light mode colors for better readability.

2. **JavaScript**:
   - Toggles the `.dark-mode` class on the `<body>` element.
   - Saves the user's preference in `localStorage`.

### Social Banner

The social banner is dynamically loaded and displayed when the page is shared:

1. **Open Graph Meta Tags**:
   - `og:image`: Specifies the banner image URL.
   - `og:title`, `og:description`: Provide context for the shared link.

2. **Dynamic Loading**:
   - The banner image is fetched and displayed based on the sharing platform.

---

## Meta Tags and SEO

The file includes Open Graph meta tags to improve social sharing:

- **Title**: "Ivy Study - Learning made free"
- **Description**: "Your go-to study platform."
- **Image**: A social banner hosted on GitHub.
- **URL**: The platform's homepage.

---

## Dark Mode

Dark mode is implemented using a combination of CSS and JavaScript:

- **CSS**:
  - Defines dark mode styles using the `.dark-mode` class.
  - Overrides light mode colors for better readability.

- **JavaScript**:
  - Toggles the `.dark-mode` class on the `<body>` element.
  - Saves the user's preference in `localStorage`.

---

## Dynamic Content Loading

The platform fetches curriculum data from a remote JSON file and processes it into a flat list of lessons. Lessons are displayed dynamically based on the selected filters and search queries.

---

## Search Functionality

The search bar provides real-time suggestions and results:

1. **Suggestions**:
   - Displays popular searches and matching lessons.

2. **Results**:
   - Filters lessons based on the search query.
   - Highlights matching terms in the results.

---

## Lesson Modal

The lesson modal displays detailed content for each lesson:

- **Markdown Rendering**:
  - Converts Markdown to HTML using Markdown-it.
  - Supports GitHub Flavored Markdown (GFM) features.

- **LaTeX Rendering**:
  - Renders mathematical equations using KaTeX.

- **Navigation**:
  - Includes "Previous" and "Next" buttons for navigating between lessons.

---

## Social Banner

The social banner is dynamically loaded and displayed when the page is shared. The banner image is hosted on GitHub and linked using the `og:image` meta tag.

---

## License
- **Code License:** MIT License (see `LICENSE`)
- **Content License:** CC BY-NC-SA 4.0 (see `LICENSE-CONTENT`)

---
