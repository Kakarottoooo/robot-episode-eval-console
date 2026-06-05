# Physical Robot Integration Plan

The MVP does not assume real hardware. To integrate XLeRobot or a physical manipulator, implement an adapter that exposes the same loop shape used by `MockRobotEnv`.

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

## First Real Tasks

- `move_to_target`
- `pick_cube`
- `place_cube`
- `button_press`
- `object_push`

Avoid dexterous manipulation until logging, reset, safety, and labeling are reliable.
