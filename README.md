![SocialBanner](https://github.com/user-attachments/assets/ca667a8a-068a-4045-b40b-5143cf29b10f)
# IVYSTUDY

Welcome to **IVYSTUDY**, a dynamic and interactive study platform designed to provide free access to lessons and study materials. This documentation explains the structure and functionality of IVYSTUDY.

---

## Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [File Structure](#file-structure)
4. [HTML Structure](#html-structure)
5. [CSS Styling](#css-styling)
6. [JavaScript Functionality](#javascript-functionality)
7. [Meta Tags and SEO](#meta-tags-and-seo)
8. [Dark Mode](#dark-mode)
9. [Dynamic Content Loading](#dynamic-content-loading)
10. [Search Functionality](#search-functionality)
11. [Lesson Modal](#lesson-modal)
12. [Social Banner](#social-banner)
13. [License](#license)

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

This project is licensed under the terms specified in the `LICENSE` file. Please refer to it for more details.

---
