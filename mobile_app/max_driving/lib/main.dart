import 'package:flutter/gestures.dart';
import 'package:flutter/material.dart';

import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:flutter_web_plugins/url_strategy.dart';
import '/flutter_flow/flutter_flow_theme.dart';
import 'flutter_flow/flutter_flow_util.dart';
import 'package:google_fonts/google_fonts.dart';
import 'flutter_flow/nav/nav.dart';
import 'package:easy_sidemenu/easy_sidemenu.dart';
import 'index.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  GoRouter.optionURLReflectsImperativeAPIs = true;
  usePathUrlStrategy();

  await FlutterFlowTheme.initialize();

  runApp(MyApp());
}

class MyApp extends StatefulWidget {
  // This widget is the root of your application.
  @override
  State<MyApp> createState() => _MyAppState();

  static _MyAppState of(BuildContext context) =>
      context.findAncestorStateOfType<_MyAppState>()!;
}

class _MyAppState extends State<MyApp> {
  ThemeMode _themeMode = FlutterFlowTheme.themeMode;

  late AppStateNotifier _appStateNotifier;
  late GoRouter _router;
  String getRoute([RouteMatch? routeMatch]) {
    final RouteMatch lastMatch =
        routeMatch ?? _router.routerDelegate.currentConfiguration.last;
    final RouteMatchList matchList = lastMatch is ImperativeRouteMatch
        ? lastMatch.matches
        : _router.routerDelegate.currentConfiguration;
    return matchList.uri.toString();
  }

  List<String> getRouteStack() =>
      _router.routerDelegate.currentConfiguration.matches
          .map((e) => getRoute(e))
          .toList();

  @override
  void initState() {
    super.initState();

    _appStateNotifier = AppStateNotifier.instance;
    _router = createRouter(_appStateNotifier);
  }

  void setThemeMode(ThemeMode mode) => safeSetState(() {
        _themeMode = mode;
        FlutterFlowTheme.saveThemeMode(mode);
      });

  @override
  Widget build(BuildContext context) {
    return MaterialApp.router(
      title: 'MaxDriving',
      localizationsDelegates: [
        GlobalMaterialLocalizations.delegate,
        GlobalWidgetsLocalizations.delegate,
        GlobalCupertinoLocalizations.delegate,
      ],
      supportedLocales: const [Locale('en', '')],
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        brightness: Brightness.light,
        useMaterial3: false,
      ),
      darkTheme: ThemeData(
        brightness: Brightness.dark,
        useMaterial3: false,
      ),
      themeMode: _themeMode,
      routerConfig: _router,
    );
  }
}

class NavBarPage extends StatefulWidget {
  NavBarPage({Key? key, this.initialPage, this.page}) : super(key: key);

  final String? initialPage;
  final Widget? page;

  @override
  _NavBarPageState createState() => _NavBarPageState();
}

/// This is the private State class that goes with NavBarPage.
class _NavBarPageState extends State<NavBarPage> {
  String _currentPageName = 'Dashboard';
  late Widget? _currentPage;
  SideMenuController sideMenuController = SideMenuController();

  @override
  void initState() {
    super.initState();
    _currentPageName = widget.initialPage ?? _currentPageName;
    _currentPage = widget.page;
  }

  @override
  Widget build(BuildContext context) {
    final tabs = {
      'Dashboard': DashboardWidget(),
      'Settings': SettingsWidget(),
      'Session': SessionWidget(),
    };
    final currentIndex = tabs.keys.toList().indexOf(_currentPageName);

    // List for sidebar version when in landscape
    List<SideMenuItem> sidebarItems = [
      SideMenuItem(
        title: 'Dashboard',
        icon: const Icon(Icons.home),
        onTap: (index, _) {
          // go to dashboard
          safeSetState(() {
            _currentPage = null;
            _currentPageName = 'Dashboard';
            sideMenuController.changePage(index);
          });
        },
      ),
      SideMenuItem(
        title: 'Settings',
        icon: const Icon(Icons.settings),
        onTap: (index, _) {
          // go to settings
          safeSetState(() {
            _currentPage = null;
            _currentPageName = 'Settings';
            sideMenuController.changePage(index);
          });
        },
      ),
      SideMenuItem(
        title: 'Session',
        icon: const Icon(Icons.photo_camera),
        onTap: (index, _) {
          // go to session
          safeSetState(() {
            _currentPage = null;
            _currentPageName = 'Session';
            sideMenuController.changePage(index);
          });
        },
      ),
    ];

    // Check device orientation
    final orient = MediaQuery.of(context).orientation;

    // if in portrait mode, use nav bar, otherwise use drawer
    if (orient == Orientation.portrait) {
      return Scaffold(
        body: _currentPage ?? tabs[_currentPageName],
        bottomNavigationBar: BottomNavigationBar(
          currentIndex: currentIndex,
          onTap: (i) => safeSetState(() {
            _currentPage = null;
            _currentPageName = tabs.keys.toList()[i];
          }),
          backgroundColor: FlutterFlowTheme.of(context).primaryBackground,
          selectedItemColor: FlutterFlowTheme.of(context).primary,
          unselectedItemColor: FlutterFlowTheme.of(context).secondaryText,
          showSelectedLabels: false,
          showUnselectedLabels: false,
          type: BottomNavigationBarType.fixed,
          items: const <BottomNavigationBarItem>[
            BottomNavigationBarItem(
              icon: Icon(
                Icons.home_outlined,
                size: 24.0,
              ),
              activeIcon: Icon(
                Icons.home,
                size: 24.0,
              ),
              label: 'Home',
              tooltip: '',
            ),
            BottomNavigationBarItem(
              icon: Icon(
                Icons.settings_outlined,
                size: 24.0,
              ),
              activeIcon: Icon(
                Icons.settings,
                size: 24.0,
              ),
              label: '__',
              tooltip: '',
            ),
            BottomNavigationBarItem(
              icon: Icon(
                Icons.photo_camera_outlined,
                size: 24.0,
              ),
              activeIcon: Icon(
                Icons.camera_alt,
                size: 24.0,
              ),
              label: 'Home',
              tooltip: '',
            )
          ],
        ),
      );
    } else {
      print("Current page: $_currentPageName");
      return Scaffold(
        // appBar: AppBar(
        //   title: Text(_currentPageName),
        //   backgroundColor: FlutterFlowTheme.of(context).primary,
        // ),
        // drawer: Drawer(
        //   child: ListView(
        //     children: tabs.keys
        //         .map((e) => ListTile(
        //               title: Text(e),
        //               onTap: () => safeSetState(() {
        //                 _currentPage = null;
        //                 _currentPageName = e;
        //               }),
        //             ))
        //         .toList(),
        //   ),
        // ),
        body: Row(children: [
          (_currentPageName != "Session") ? SafeArea(
            child: SideMenu(
              controller: sideMenuController,
              style: SideMenuStyle(
                  displayMode: SideMenuDisplayMode.compact,
                  itemBorderRadius: const BorderRadius.all(Radius.circular(50)),
                  backgroundColor: Colors.white,
                  iconSize: 24,
                  itemOuterPadding:
                      EdgeInsets.symmetric(horizontal: 5, vertical: 25)),
              items: sidebarItems,
            ),
          ) : Container(),
          Expanded(child: _currentPage ?? tabs[_currentPageName] as Widget),
        ]),
      );
    }
  }
}
