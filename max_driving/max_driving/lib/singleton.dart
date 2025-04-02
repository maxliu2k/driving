import 'package:flutter/material.dart';

class Data extends ChangeNotifier {
  static final Data _instance = Data._internal();

  factory Data() {
    return _instance;
  }

  Data._internal();

  Map<String, dynamic> data = {};

  void notify() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      notifyListeners();
    });
  }
}
