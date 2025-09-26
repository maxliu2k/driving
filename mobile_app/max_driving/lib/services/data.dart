import 'package:shared_preferences/shared_preferences.dart';
import 'package:flutter/material.dart';

class Data extends ChangeNotifier{
  // initialize the data class
  static final Data _instance = Data._internal();
  factory Data() {
    return _instance;
  }
  Data._internal();

  // shared preferences instance
  SharedPreferences? _prefs;
  Future<void> init() async {
    _prefs = await SharedPreferences.getInstance();
  }


  // data storage
  final Map<String, dynamic> _data = {};
  dynamic get(String key) {
    return _data[key];
  }
  void set(String key, dynamic value) {
    _data[key] = value;
    _prefs?.setString(key, value.toString());
  }

  Future<void> loadData() async {
    if (_prefs != null) {
      for (String key in _prefs!.getKeys()) {
        _data[key] = _prefs!.getString(key);
      }
    }
  }

  Future<void> writeData() async {
    if (_prefs != null) {
      for (String key in _data.keys) {
        await _prefs!.setString(key, _data[key].toString());
      }
    }
  }

  // notify function
  void notify() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      notifyListeners();
    });
  }
}