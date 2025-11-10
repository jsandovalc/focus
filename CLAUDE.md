# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Focus! is an RPG-inspired productivity app that combines the Flowmodoro technique with skill development and goal tracking. It's built with Python, using PySide6 (Qt6) for the GUI, SQLModel for database operations, and uses a service-oriented architecture.

## Core Architecture

The application follows a layered architecture:

### Domain Layer (`domain.py`)
- **Skill**: Core skill system with XP, leveling, and stat relationships
- **Stat**: Character attributes (intellect, willpower, dexterity, vitality, charisma, strength, wisdom)  
- **Goal**: Tasks tied to skills with difficulty-based XP rewards

### Data Layer
- **`repositories.py`**: Data access layer using SQLModel/SQLAlchemy
- **`db.py`**: Database initialization and table creation
- **`models.py`**: Database model definitions

### Service Layer (`services.py`)
- **SkillsService**: Handles XP granting, skill creation, and stat updates
- **GoalsService**: Manages goal completion logic

### UI Layer (`main.py`)
- **FocusMainWindow**: Main PySide6 QMainWindow with tabbed interface (Timer, Stats, Skills, Goals)
- **NewSkillDialog, NewGoalDialog, LevelUpDialog**: Qt modal dialogs for user interactions
- **Signal Bridge**: Bridges Blinker signals to Qt signals for thread-safe UI updates
- **Focus**: Core business logic and timer management (`focus.py`)
- **Timer**: Time tracking utilities (`timer.py`)

**Note**: The old Toga implementation is preserved as `main_toga.py` for reference.

### Supporting Modules
- **`signals.py`**: Event-driven communication using Blinker
- **`enums.py`**: Application enumerations (Difficulty levels)
- **`conf.py`**: Configuration constants

## Development Commands

### Running the Application
```bash
uv run main.py
```

### Development Dependencies
The project uses `uv` for dependency management. Development dependencies include:
- **pytest**: Testing framework
- **ruff**: Linting and formatting  
- **mypy**: Type checking
- **devtools**: Development utilities

### Testing
```bash
uv run pytest                    # Run all tests
uv run pytest test_skills.py    # Run specific test file
uv run pytest -v                # Verbose output
```

### Code Quality
```bash
uv run ruff check --fix         # Lint code with auto-fixes
uv run ruff format              # Format code
uv run mypy .                   # Type checking
```

**Standards**: Always run these commands before committing changes to ensure code quality and consistency.

## Key Concepts

### Flowmodoro System
- Users focus for flexible periods, earning break time at a 5:1 ratio (configurable via `BREAK_RATIO`)
- XP is granted based on focus time when switching to break mode
- Break time can go negative (overtime) with visual/audio notifications

### Skill System
- Skills have main and optional secondary stats
- Leveling increases stats (main +2, secondary +1)  
- XP requirements increase by 1.5x per level
- Skills gain XP from focus sessions and goal completion

### Goal System
- Goals have difficulty levels (easy/medium/hard/project) with different XP rewards
- Goals have priority levels (urgent/high/medium/low) for organization and display ordering
- Completion grants XP to associated skills
- Goals can have main and secondary skills

### Signal-Driven Architecture
The app uses Blinker signals for loose coupling between business logic and UI:
- `xp_gained`: Fired when XP is awarded
- `level_gained`: Fired when skill levels up
- `goal_added`/`goal_completed`: Goal lifecycle events

**Qt Signal Bridge**: The UI bridges Blinker signals to Qt signals (QTimer-based) to ensure thread-safe UI updates. Blinker signals from the service layer are caught by bridge methods and re-emitted as Qt signals that connect to UI update handlers.

## Database Schema

The app uses SQLite with SQLModel. Key relationships:
- Skills reference Stats (main/secondary)
- Goals reference Skills (main/secondary)  
- All entities have repository classes for data access

## Configuration

Core settings in `conf.py`:
- `POMODORO_BLOCK_SIZE`: Base time unit (25 minutes)
- `BASE_XP`/`CAP_XP_AT`: XP calculation parameters
- `BREAK_RATIO`: Focus to break time ratio
- `PRIORITY_ORDER`: Goal sorting order configuration
- `PRIORITY_COLORS`: UI color scheme for priority levels

## Testing Strategy

Tests are organized by module with fixtures in `conftest.py`. The test suite covers:
- Domain logic (skill leveling, goal completion)
- Service layer operations
- Timer functionality
- Repository data access

Use freezegun for time-based testing and pytest-mock for mocking dependencies.

## Architecture Patterns

### Service Layer Pattern
Follow proper separation of concerns between layers:
- **UI Layer** (`main.py`): Display and user interaction only
- **Service Layer** (`services.py`): Business logic and data operations  
- **Repository Layer** (`repositories.py`): Data access and persistence
- **Domain Layer** (`domain.py`): Core business entities and rules

**Example**: Goal sorting logic belongs in `GoalsService.get_goals_by_priority()`, not in UI code.

### Configuration Management
All application constants should be centralized in `conf.py`:
- Never hardcode values in UI or business logic
- Use descriptive constant names with comments
- Group related constants together (e.g., priority system, XP calculations)
- Import constants where needed rather than duplicating values

### Database Migrations
Use the migration system in `db.py` for schema changes:
- Check for column existence before adding new fields
- Provide default values for backward compatibility  
- Update existing data when enum values change
- Always preserve user data during migrations

## Priority System

Goals use a 4-level priority system for organization:

### Priority Levels
- **URGENT**: Highest priority (red) - immediate attention required
- **HIGH**: Important tasks (orange) - should be completed soon  
- **MEDIUM**: Default priority (blue) - normal workflow
- **LOW**: Lowest priority (gray) - nice to have

### Implementation
- **Configuration**: `PRIORITY_ORDER` and `PRIORITY_COLORS` in `conf.py`
- **Sorting**: Goals display in priority order (urgent → high → medium → low)  
- **UI**: Color-coded priority indicators in goals table
- **Database**: Priority column with migration support for existing data
- Use Qt and PySide6 best practices.