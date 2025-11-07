import 'dart:convert';
import 'dart:typed_data';

// import 'package:image_picker/image_picker.dart';
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

  // Future<void> loadData() async {
  //   if (_prefs != null) {
  //     for (String key in _prefs!.getKeys()) {
  //       _data[key] = _prefs!.getString(key);
  //     }
  //   }
  // }

  // Future<void> writeData() async {
  //   if (_prefs != null) {
  //     for (String key in _data.keys) {
  //       await _prefs!.setString(key, _data[key].toString());
  //     }
  //   }
  // }


  static Future<void> saveData(String key, dynamic value) async {
    final prefs = await SharedPreferences.getInstance();
    if (value is String) {
      await prefs.setString(key, value);
    } else if (value is int) {
      await prefs.setInt(key, value);
    } else if (value is bool) {
      await prefs.setBool(key, value);
    } else if (value is double) {
      await prefs.setDouble(key, value);
    } else if (value is List<String>) {
      await prefs.setStringList(key, value);
    } 
    // else if (value is XFile) {
    //   // Convert image data to byte string
    //   print("Image Path: ${value.readAsBytes()}");
    //   Uint8List imageData = await value.readAsBytes();
    //   String base64String = base64Encode(imageData);
    //   print("Byte String Length: ${base64String.length}");
    //   await prefs.setString(key, base64String);
    // } 
    else {
      throw Exception("Unsupported value type");
    }
  }

  static Future<dynamic> getData(String key) async {
    final prefs = await SharedPreferences.getInstance();
    // dynamic value = prefs.get(key);
    // Check if bytestring
    // if (value is String && value.isNotEmpty && (value.length > 1000)) {
    //   Uint8List imageData = base64Decode(value);
    //   return XFile.fromData(imageData, name: "profile_image.png");
    // }
    return prefs.get(key);
  }

  static Future<void> removeData(String key) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(key);
  }

  // notify function
  void notify() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      notifyListeners();
    });
  }
}