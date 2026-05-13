from manimator.utils.helpers import read_base64_few_shot_file

FOURIER_TRANSFORM_EXAMPLE = [
    {
        "role": "user",
        "content": "Fourier Transform",
    },
    {
        "role": "assistant",
        "content": r"""### *Topic*: Fourier Transform
*Key Points*:
- Time domain vs frequency domain
- Decomposing signals into sine waves: \( f(t) = \sum_{n} A_n \sin(2\pi n t + \phi_n) \)
- Fourier Transform formula: \( \hat{f}(\xi) = \int_{-\infty}^{\infty} f(t) e^{-2\pi i \xi t} dt \)
- Applications in signal processing
*Visual Elements*:
- Animate a complex signal being decomposed into sine waves.
- Show the Fourier Transform as a graph in the frequency domain.
*Style*: Smooth animations with mathematical formulas and graphs.""",
    },
]

GRADIENT_DESCENT_EXAMPLE = [
    {
        "role": "user",
        "content": "Explain Gradient Descent",
    },
    {
        "role": "assistant",
        "content": r"""### *Topic*: Gradient Descent
*Key Points*:
- Loss function: \( L(\theta) = \frac{1}{N} \sum_{i=1}^{N} (y_i - f(x_i; \theta))^2 \)
- Gradient calculation: \( \nabla L(\theta) = \frac{\partial L}{\partial \theta} \)
- Update rule: \( \theta_{new} = \theta_{old} - \alpha \nabla L(\theta) \)
- Convergence to the minimum
*Visual Elements*:
- 3D surface plot of the loss function.
- Animate the gradient descent steps moving toward the minimum.
*Style*: 3D visualizations with step-by-step explanations.""",
    },
]

BACKPROPOGATION_EXAMPLE = [
    {
        "role": "user",
        "content": "How does backpropogation work in neural networks?",
    },
    {
        "role": "assistant",
        "content": r"""### *Topic*: Neural Networks (Backpropagation)
*Key Points*:
- Loss function: \( L(\theta) = \frac{1}{N} \sum_{i=1}^{N} (y_i - f(x_i; \theta))^2 \)
- Chain rule: \( \frac{\partial L}{\partial f} \frac{\partial f}{\partial \theta} \)
- Weight updates: \( \theta_{new} = \theta_{old} - \alpha \nabla L(\theta) \)
*Visual Elements*:
- Animate the flow of gradients through the network.
- Show the loss surface and gradient descent steps.
*Style*: Step-by-step, with clear visualizations of gradients and updates.""",
    },
]

SCENE_EXAMPLES = [
    message
    for example in [
        FOURIER_TRANSFORM_EXAMPLE,
        GRADIENT_DESCENT_EXAMPLE,
        BACKPROPOGATION_EXAMPLE,
    ]
    for message in example
]

few_shot_pdf = read_base64_few_shot_file()

PDF_EXAMPLE = {
    "role": "user",
    "content": [
        {
            "type": "image_url",
            "image_url": "data:application/pdf;base64,{}".format(few_shot_pdf),
        },
    ],
}, {
    "role": "assistant",
    "content": r"""*Topic*: Deep Residual Learning for Image Recognition
*Key Points*:
1. *Degradation Problem*: Explain how deeper networks suffer from higher training error despite having more capacity.
2. *Residual Learning*: Show how residual learning reformulates the problem by learning residual functions \( \mathcal{F}(\mathbf{x}) = \mathcal{H}(\mathbf{x}) - \mathbf{x} \) instead of direct mappings \( \mathcal{H}(\mathbf{x}) \).
3. *Shortcut Connections*: Visualize how identity shortcuts (skip connections) are added to the network to enable residual learning.
4. *Deep Residual Networks*: Demonstrate the architecture of deep residual networks (e.g., ResNet-34, ResNet-152) and how they outperform plain networks.
5. *Bottleneck Design*: Explain the bottleneck design in deeper ResNets (e.g., ResNet-50/101/152) using \(1 \times 1\), \(3 \times 3\), and \(1 \times 1\) convolutions.

*Style*: 3Blue1Brown style (clean, minimalistic, with smooth animations and clear labels)
*Additional Requirements*:
- Include mathematical formulas (e.g., \( \mathcal{F}(\mathbf{x}) = \mathcal{H}(\mathbf{x}) - \mathbf{x} \)) and graphs (e.g., training error vs. depth).
- Use color coding to differentiate between plain networks and residual networks.
- Animate the flow of data through shortcut connections and residual blocks.
- Provide step-by-step explanations for each concept.""",
}
