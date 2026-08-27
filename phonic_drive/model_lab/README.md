# Model Lab

`phonic_drive.model_lab` is an optional simulation sandbox for testing whether simple local dynamical rules can generate structures resembling motifs measured by Phonic Drive.

## What belongs here

Candidate simulation abstractions include:

- boid-like moving agents
- energy-transfer agents
- scalar/vector fields
- reaction-diffusion systems
- excitation and decay
- attraction / repulsion / alignment
- scattering
- saturation
- refractory periods
- hysteresis / state memory

A generic abstraction may use:

```text
B_i(t) = moving interaction / energy agent
C(x,t) = stateful substrate or field
```

with local updates such as:

```text
B_i + C -> B_i' + C'
```

## What does not belong here

Model Lab output is not automatically:

- a photon simulation;
- a biochemical simulation;
- a neural simulation;
- evidence that a participant response was caused by the simulated mechanism.

Terms such as "photon-boid" may be useful as conceptual model labels, but implementation and documentation must identify when a rule is metaphorical, abstract, physically constrained, or empirically parameterized.

## Why isolate Model Lab

The empirical Phonic Drive pipeline measures audio and records participant/behavioral observations. Simulation is a different epistemic object.

Keeping Model Lab separate lets us ask useful questions such as:

> Can a small set of local interaction rules generate convergence, branching, oscillation, release, hysteresis, or other topology resembling motifs found in measured acoustic trajectories?

without replacing evidence with analogy.

## Interface with the motif engine

Model Lab should exchange **structural descriptors**, not causal labels.

```text
measured audio -> A(t) -> M_audio(t)
                         ^
                         |
synthetic rules -> S(t) -> M_sim(t)
```

Comparison operates on motif geometry, recurrence, transition ordering, duration, and other defined descriptors.

A similarity result means the structures resemble each other under the chosen metric. It does not establish shared physical mechanism.
