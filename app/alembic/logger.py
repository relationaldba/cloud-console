import sqlalchemy as sa


def log_migration(conn, schema_version, step, description, started_at, execution_duration=None, success=True, error=None):
    """Helper function to log a migration step."""
    conn.execute(
        sa.text(
            "INSERT INTO schema_change_history (schema_version, step, description, started_at, execution_duration, success, error) "
            "VALUES (:schema_version, :step, :description, :started_at, :execution_duration, :success, :error)"
        ),
        {
            "schema_version": schema_version,
            "step": step,
            "description": description,
            "started_at": started_at,
            "execution_duration": execution_duration,
            "success": success,
            "error": error,
        },
    )
