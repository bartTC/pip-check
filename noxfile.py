import nox

nox.options.default_venv_backend = "uv"

python_versions = ["3.8", "3.9", "3.10", "3.11", "3.12", "3.13"]


@nox.session(python=python_versions)
def tests(session):
    session.install("--upgrade", "pip", "uv")
    session.install("html5lib==0.999999999", "django==1.10", "pyglet==2.0.dev23")
    session.install(".")  # Assuming pip-check is in the current project

    session.run("pip-check")
    session.run("pip-check", "--help")
    session.run(
        "pip-check",
        "--ascii",
        "--not-required",
        "--full-version",
        "--hide-unchanged",
        "--show-update",
    )
    session.run("pip-check", "--user")
    session.run("pip-check", "--local")

    session.run("pip-check", "--cmd=uv pip")
    session.run("pip-check", "--cmd=uv pip", "--help")
    session.run(
        "pip-check", "--cmd=uv pip", "--ascii", "--full-version", "--hide-unchanged"
    )


@nox.session
def readme(session):
    session.install("markdown-it-py")
    session.run("markdown-it", "README.md", "/dev/null", external=True)
