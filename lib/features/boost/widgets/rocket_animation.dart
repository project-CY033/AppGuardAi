import 'package:flutter/material.dart';

class RocketAnimation extends StatefulWidget {
  final bool isAnimating;
  final bool isResult;

  const RocketAnimation({
    super.key,
    required this.isAnimating,
    required this.isResult,
  });

  @override
  State<RocketAnimation> createState() => _RocketAnimationState();
}

class _RocketAnimationState extends State<RocketAnimation> with TickerProviderStateMixin {
  late AnimationController _shakeController;
  late AnimationController _flameController;
  late AnimationController _takeoffController;
  
  late Animation<double> _shakeAnimation;
  late Animation<double> _takeoffAnimation;

  @override
  void initState() {
    super.initState();
    
    _shakeController = AnimationController(
       vsync: this,
       duration: const Duration(milliseconds: 50),
    );

    _shakeAnimation = Tween<double>(begin: -2.0, end: 2.0).animate(_shakeController);

    _flameController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 300),
    );

    _takeoffController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 800),
    );

    _takeoffAnimation = Tween<double>(begin: 0.0, end: -800.0).animate(
      CurvedAnimation(parent: _takeoffController, curve: Curves.easeInExpo)
    );
  }

  @override
  void didUpdateWidget(RocketAnimation oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (widget.isAnimating && !oldWidget.isAnimating) {
      _shakeController.repeat(reverse: true);
      _flameController.repeat(reverse: true);
    } else if (!widget.isAnimating && oldWidget.isAnimating) {
      _shakeController.stop();
      _flameController.stop();
    }

    if (widget.isResult && !oldWidget.isResult) {
       _shakeController.stop();
       _flameController.stop();
       _takeoffController.forward();
    }
    
    if (!widget.isAnimating && !widget.isResult) {
      _takeoffController.reset();
    }
  }

  @override
  void dispose() {
    _shakeController.dispose();
    _flameController.dispose();
    _takeoffController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: Listenable.merge([_shakeController, _flameController, _takeoffController]),
      builder: (context, child) {
        double shakeX = widget.isAnimating ? _shakeAnimation.value : 0;
        double offsetY = _takeoffController.isAnimating || widget.isResult ? _takeoffAnimation.value : 0;

        return Transform.translate(
          offset: Offset(shakeX, offsetY),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              // The Rocket
              Container(
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  boxShadow: widget.isAnimating ? [
                    BoxShadow(
                      color: Colors.blueAccent.withValues(alpha: 0.5),
                      blurRadius: 40,
                      spreadRadius: 10,
                    )
                  ] : [],
                ),
                child: ShaderMask(
                  shaderCallback: (bounds) => const LinearGradient(
                    colors: [Colors.cyan, Colors.blueAccent, Colors.purpleAccent],
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                  ).createShader(bounds),
                  child: const Icon(
                    Icons.rocket_launch_rounded,
                    size: 150,
                    color: Colors.white,
                  ),
                ),
              ),
              
              // Flame/Exhaust Engine
              if (widget.isAnimating || (_takeoffController.isAnimating && !widget.isResult))
                CustomPaint(
                  size: const Size(80, 100),
                  painter: FlamePainter(animationValue: _flameController.value),
                ),
            ],
          ),
        );
      },
    );
  }
}

class FlamePainter extends CustomPainter {
  final double animationValue;
  
  FlamePainter({required this.animationValue});

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
       ..shader = LinearGradient(
         colors: [Colors.orange, Colors.deepOrangeAccent, Colors.redAccent.withValues(alpha: 0.0)],
         begin: Alignment.topCenter,
         end: Alignment.bottomCenter,
       ).createShader(Rect.fromLTWH(0, 0, size.width, size.height + (animationValue * 20)));
    
    final path = Path();
    path.moveTo(size.width * 0.3, 0); // Left nozzle
    path.lineTo(size.width * 0.7, 0); // Right nozzle
    
    // Flame tip fluctuates with animation
    final flameLength = size.height * 0.6 + (animationValue * size.height * 0.4);
    
    path.quadraticBezierTo(
      size.width * 0.5, flameLength, 
      size.width * 0.5, flameLength,
    );
    path.close();

    canvas.drawPath(path, paint);
    
    // Core Flame
    final corePaint = Paint()
       ..color = Colors.yellowAccent.withValues(alpha: 0.8)
       ..maskFilter = const MaskFilter.blur(BlurStyle.normal, 10);
    
    final corePath = Path();
    corePath.moveTo(size.width * 0.4, 0);
    corePath.lineTo(size.width * 0.6, 0);
    final coreLength = size.height * 0.3 + (animationValue * size.height * 0.2);
    corePath.quadraticBezierTo(size.width * 0.5, coreLength, size.width * 0.5, coreLength);
    corePath.close();
    
    canvas.drawPath(corePath, corePaint);
  }

  @override
  bool shouldRepaint(covariant FlamePainter oldDelegate) => true;
}
