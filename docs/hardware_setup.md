# Physical Robot Integration Plan

The MVP does not assume real hardware. To integrate XLeRobot or a physical manipulator, implement an adapter that exposes the same loop shape used by `MockRobotEnv`.

The repository now includes a Phase 7 skeleton:

```text
robot/adapters/physical_arm_adapter.py
robot/safety/checks.py
scripts/safety_check_example.py
scripts/label_episode.py
tests/test_safety_checks.py
```

## Adapter Contract

```python
state = env.reset()
while not done:
    action = policy.act(state)
    next_state, reward, done, info = env.step(action)
    frame = env.render_frame()
    recorder.record_step(
        frame=frame,
        state=state,
        action=action,
        reward=reward,
        timestamp=timestamp,
    )
    state = next_state
```

`PhysicalArmAdapter` intentionally raises `NotImplementedError` for actual hardware I/O. A real integration should subclass it and implement:

- `_read_observation()` for joint state, TCP pose, timestamps, and camera frames
- `_send_action(action)` for command publishing
- `_wait_for_manual_reset()` for operator confirmation between trials

## Required Safety Gates

- Validate joint limits before sending commands.
- Clamp max velocity and acceleration.
- Enforce torque/force limits where hardware exposes them.
- Enforce a workspace boundary.
- Keep an emergency stop within reach.
- Start in low-speed mode.
- Add manual reset steps between trials.
- Validate camera frames and robot state freshness.
- Require manual success/failure labels for early real-world trials.

The `SafetyChecker` provides the first software safety layer:

```python
from robot.safety import SafetyChecker, SafetyConfig

checker = SafetyChecker(SafetyConfig.default(action_dim=4, joint_dim=8))
result = checker.prepare_action([0.5, -0.4, 0.05, 0.0])
```

It currently covers:

- emergency stop blocking
- action clipping
- low-speed scaling
- joint position limits
- joint velocity limits
- workspace bounds

Run the local tests:

```powershell
python -m unittest discover -s tests
python scripts\safety_check_example.py
```

## Manual Labeling

Early real-world trials should require a human success/failure decision. Update one saved episode with:

```powershell
python scripts\label_episode.py --episode-id episode_000001 --success true
python scripts\label_episode.py --episode-id episode_000002 --success false --failure-reason collision
```

By default, the script updates `metadata.json` and tries to sync the metadata row to the configured database. Use `--skip-db` to update only the file or `--require-db` to fail unless PostgreSQL sync succeeds.

## Real Adapter Implementation Steps

1. Create a subclass such as `XLeRobotArmAdapter`.
2. Map hardware state into `RobotObservation`.
3. Route every proposed command through `SafetyChecker.prepare_action()`.
4. Start with low-speed mode and a small workspace boundary.
5. Record episodes through `EpisodeRecorder` with `environment="real_robot"`.
6. Label each trial with `scripts/label_episode.py`.
7. Review failure reasons in the web console before increasing speed or task complexity.

## First Real Tasks

- `move_to_target`
- `pick_cube`
- `place_cube`
- `button_press`
- `object_push`

Avoid dexterous manipulation until logging, reset, safety, and labeling are reliable.
