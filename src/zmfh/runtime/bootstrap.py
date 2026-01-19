"""ZMFH bootstrap.

Called automatically via `sitecustomize`.

Hard rules:
- never raise
- minimal side effects
- idempotent
"""

from __future__ import annotations

from zmfh.runtime.state import get_state


def bootstrap() -> None:
    st = get_state()
    if st.bootstrapped:
        return

    try:
        from zmfh.runtime.env import read_env

        cfg = read_env()
        st.disabled = cfg.disabled
        st.diag = cfg.diag
        st.mode = cfg.mode
        st.policy_path = cfg.policy_path
        st.trace_file = getattr(cfg, "trace_file", None)
        st.root = cfg.root
        st.roots = list(cfg.roots)

        if st.disabled or getattr(st.mode, "value", str(st.mode)) == "off":
            st.bootstrapped = True
            return

        # Load policy (optional)
        try:
            from zmfh.policy.defaults import default_policy
            from zmfh.policy.load import load_policy

            pol = default_policy()
            if cfg.policy_path:
                pol = load_policy(cfg.policy_path, fallback=pol)
            setattr(st, "_policy", pol)

            # If the user did not explicitly set ZMFH_MODE, allow the policy file
            # to drive the runtime mode (so policy "mode" is not ignored).
            try:
                import os
                from zmfh._constants import ENV_MODE

                if os.environ.get(ENV_MODE) is None:
                    st.mode = getattr(pol, "mode", st.mode)
            except Exception:
                pass

            # If the user did not explicitly set ZMFH_ROOT, allow the policy file
            # to provide roots.
            try:
                import os
                from pathlib import Path

                from zmfh._constants import ENV_ROOT

                if os.environ.get(ENV_ROOT) is None:
                    proots = list(getattr(pol, "roots", []) or [])
                    norm: list[str] = []
                    for r in proots:
                        s = str(r).strip()
                        if not s:
                            continue
                        try:
                            norm.append(str(Path(s).expanduser().resolve()))
                        except Exception:
                            norm.append(s)
                    if norm:
                        st.roots = norm
                        st.root = norm[0]
            except Exception:
                pass
        except Exception as e:
            st.last_error = f"policy_load_failed: {e!r}"

        # Install import hook
        try:
            from zmfh.hook.install import install_meta_path_hook

            finder = install_meta_path_hook()
            st.hook_installed = finder is not None
        except Exception as e:
            st.last_error = f"hook_install_failed: {e!r}"

        st.bootstrapped = True

        # Diagnostic event
        try:
            from zmfh.evidence.log import emit

            emit("bootstrap", "bootstrapped", root=st.root, mode=getattr(st.mode, "value", str(st.mode)))
        except Exception:
            pass

    except Exception as e:
        st.last_error = f"bootstrap_failed: {e!r}"
        st.bootstrapped = True
        return
