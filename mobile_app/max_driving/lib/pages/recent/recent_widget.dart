import '/flutter_flow/flutter_flow_charts.dart';
import '/flutter_flow/flutter_flow_icon_button.dart';
import '/flutter_flow/flutter_flow_theme.dart';
import '/flutter_flow/flutter_flow_util.dart';
import '/flutter_flow/flutter_flow_widgets.dart';
import 'dart:math';
import 'dart:ui';
import '/flutter_flow/random_data_util.dart' as random_data;
import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:provider/provider.dart';
import 'recent_model.dart';
import 'package:max_driving/services/data.dart';
export 'recent_model.dart';
import 'package:easy_sidemenu/easy_sidemenu.dart';
// import 'package:flutter_flow/flutter_flow_util.dart';

class RecentWidget extends StatefulWidget {
  const RecentWidget({super.key});

  static String routeName = 'Recent';
  static String routePath = '/recent';

  @override
  State<RecentWidget> createState() => _RecentWidgetState();
}

class _RecentWidgetState extends State<RecentWidget> {
  late RecentModel _model;

  final scaffoldKey = GlobalKey<ScaffoldState>();

  // Score Data
  List<dynamic> scoreXData = List.generate(
    30,
    (index) => index + 1,
  );
  // List<dynamic> scoreYData = List.generate(
  //   30,
  //   (index) => index == 0 ? 90 : Random().nextInt(100),
  // );
  List<int> scoreYData = [
    85,
    92,
    86,
    88,
    89,
    88,
    86,
    91,
    89,
    89,
    90,
    90,
    88,
    92,
    91,
    89,
    91,
    93,
    92,
    91,
    90,
    93,
    91,
    95,
    92,
    94,
    95,
    96,
    93,
    95
  ];

  // Red Lights Data
  List<dynamic> redLightsXData = List.generate(
    30,
    (index) => index + 1,
  );
  // List<dynamic> redLightsYData = List.generate(
  //   30,
  //   (index) => index == 0 ? 1 : Random().nextInt(5),
  // );
  List<int> redLightsYData = [
    2,
    0,
    1,
    1,
    1,
    0,
    2,
    0,
    1,
    0,
    0,
    1,
    0,
    1,
    0,
    1,
    0,
    0,
    1,
    0,
    1,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0
  ];

  // Stop Signs Data
  List<dynamic> stopSignsXData = List.generate(
    30,
    (index) => index + 1,
  );
  // List<dynamic> stopSignsYData = List.generate(
  //   30,
  //   (index) => index == 0 ? 2 : Random().nextInt(5),
  // );

  List<int> stopSignsYData = [
    3,
    2,
    1,
    2,
    1,
    2,
    3,
    2,
    1,
    2,
    1,
    3,
    2,
    1,
    1,
    2,
    0,
    2,
    0,
    1,
    0,
    1,
    0,
    2,
    0,
    0,
    1,
    0,
    1,
    1
  ];

  // Speed Limit Violations Data
  List<dynamic> speedingXData = List.generate(
    30,
    (index) => index + 1,
  );
  // List<dynamic> speedingYData = List.generate(
  //   30,
  //   (index) => index == 0 ? 0 : Random().nextInt(5),
  // );
  List<int> speedingYData = [
    3,
    1,
    2,
    2,
    3,
    1,
    2,
    1,
    1,
    0,
    1,
    2,
    2,
    2,
    0,
    1,
    2,
    0,
    1,
    0,
    2,
    0,
    2,
    1,
    1,
    0,
    1,
    1,
    1,
    0
  ];

  // Turning Data
  List<dynamic> turningXData = List.generate(
    30,
    (index) => index + 1,
  );
  // List<dynamic> turningYData = List.generate(
  //   30,
  //   (index) => index == 0 ? 1 : Random().nextInt(5),
  // );
  List<int> turningYData = [
    3,
    2,
    2,
    1,
    2,
    1,
    3,
    1,
    1,
    0,
    2,
    1,
    2,
    1,
    0,
    2,
    1,
    0,
    1,
    0,
    1,
    0,
    0,
    0,
    0,
    1,
    0,
    0,
    1,
    1
  ];

  List<Map<String, dynamic>> recentSessions = [
    {
      'sessionTime': '15 mins',
      'lightsRan': 0,
      'stopSignsMissed': 1,
      'speedViolations': 1,
      'turnSignalsMissed': 1,
      'score': 93,
    },
    {
      'sessionTime': '20 mins',
      'lightsRan': 0,
      'stopSignsMissed': 1,
      'speedViolations': 0,
      'turnSignalsMissed': 1,
      'score': 95,
    },
  ];

  SideMenuController sideMenuController = SideMenuController();
  String _currentPageName = 'Dashboard';
  late Widget? _currentPage;

  @override
  void initState() {
    super.initState();
    _model = createModel(context, () => RecentModel());
  }

  @override
  void dispose() {
    _model.dispose();

    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    // List<SideMenuItem> sidebarItems = [
    //   // TODO: fix tab behaviour to move to other screens
    //   SideMenuItem(
    //     title: 'Dashboard',
    //     icon: const Icon(Icons.home),
    //     onTap: (index, _) {
    //       print('Dashboard tapped going to idx: $index');
    //       // go to dashboard
    //       safeSetState(() {
    //         _currentPage = null;
    //         _currentPageName = 'Dashboard';
    //         sideMenuController.changePage(index);
    //       });
    //     },
    //   ),
    //   SideMenuItem(
    //     title: 'Settings',
    //     icon: const Icon(Icons.settings),
    //     onTap: (index, _) {
    //       print('Settings tapped going to idx: $index');
    //       // go to settings
    //       safeSetState(() {
    //         _currentPage = null;
    //         _currentPageName = 'Settings';
    //         sideMenuController.changePage(index);
    //       });
    //     },
    //   ),
    //   SideMenuItem(
    //     title: 'Session',
    //     icon: const Icon(Icons.photo_camera),
    //     onTap: (index, _) {
    //       print('Session tapped going to idx: $index');
    //       // go to session
    //       safeSetState(() {
    //         _currentPage = null;
    //         _currentPageName = 'Session';
    //         sideMenuController.changePage(index);
    //       });
    //     },
    //   ),
    // ];
    // Check device orientation
    final orient = MediaQuery.of(context).orientation;

    return GestureDetector(
      onTap: () {
        FocusScope.of(context).unfocus();
        FocusManager.instance.primaryFocus?.unfocus();
      },
      child: Scaffold(
        key: scaffoldKey,
        backgroundColor: Color(0xFFAFABFF),
        appBar: (orient == Orientation.portrait)
            ? AppBar(
                backgroundColor: Colors.white,
                automaticallyImplyLeading: false,
                leading: FlutterFlowIconButton(
                  borderColor: Colors.transparent,
                  borderRadius: 30.0,
                  buttonSize: 46.0,
                  icon: Icon(
                    Icons.arrow_back_rounded,
                    color: Color(0xFF14181B),
                    size: 25.0,
                  ),
                  onPressed: () async {
                    context.pop();
                  },
                ),
                title: Text(
                  'Recent Activity',
                  style: FlutterFlowTheme.of(context).headlineMedium.override(
                        fontFamily: 'Outfit',
                        letterSpacing: 0.0,
                      ),
                ),
                actions: [],
                centerTitle: false,
                elevation: 0.0,
              )
            : null,
        body: Row(
          children: [
            // if (orient != Orientation.portrait)
            //   SideMenu(
            //     controller: sideMenuController,
            //     style: SideMenuStyle(
            //         displayMode: SideMenuDisplayMode.compact,
            //         itemBorderRadius: const BorderRadius.all(Radius.circular(50)),
            //         backgroundColor: Colors.white,
            //         iconSize: 24,
            //         itemOuterPadding:
            //             EdgeInsets.symmetric(horizontal: 5, vertical: 25)),
            //     items: sidebarItems,
            //   ),
            Expanded(
              child: SafeArea(
                top: true,
                child: SingleChildScrollView(
                  child: Column(
                    mainAxisSize: MainAxisSize.max,
                    children: [
                      // Embedded Appbar
                      if (orient != Orientation.portrait)
                      Padding(
                        padding: const EdgeInsetsDirectional.fromSTEB(
                            0.0, 0.0, 0.0, 12.0),
                        child: AppBar(
                          backgroundColor: Colors.white,
                          automaticallyImplyLeading: false,
                          leading: FlutterFlowIconButton(
                            borderColor: Colors.transparent,
                            borderRadius: 30.0,
                            buttonSize: 46.0,
                            icon: const Icon(
                              Icons.arrow_back_rounded,
                              color: Color(0xFF14181B),
                              size: 25.0,
                            ),
                            onPressed: () async {
                              context.pop();
                            },
                          ),
                          title: Text(
                            'Recent Activity',
                            style:
                                FlutterFlowTheme.of(context).headlineMedium.override(
                                      fontFamily: 'Outfit',
                                      letterSpacing: 0.0,
                                    ),
                          ),
                          actions: [],
                          centerTitle: false,
                          elevation: 0.0,
                        ),
                      ),
                      Align(
                        alignment: AlignmentDirectional(0.0, 0.0),
                        child: Padding(
                          padding: EdgeInsetsDirectional.fromSTEB(
                              16.0, 12.0, 16.0, 15.0),
                          child: Container(
                            decoration: BoxDecoration(
                              color: Colors.white,
                              boxShadow: [
                                BoxShadow(
                                  blurRadius: 3.0,
                                  color: Color(0x33000000),
                                  offset: Offset(
                                    0.0,
                                    1.0,
                                  ),
                                )
                              ],
                              borderRadius: BorderRadius.circular(12.0),
                            ),
                            child: Padding(
                              padding: EdgeInsetsDirectional.fromSTEB(
                                  0.0, 0.0, 0.0, 12.0),
                              child: Column(
                                mainAxisSize: MainAxisSize.max,
                                mainAxisAlignment: MainAxisAlignment.start,
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Padding(
                                    padding: EdgeInsetsDirectional.fromSTEB(
                                        16.0, 12.0, 0.0, 4.0),
                                    child: Text(
                                      'Previous Session Info',
                                      style: FlutterFlowTheme.of(context)
                                          .headlineMedium
                                          .override(
                                            fontFamily: 'Outfit',
                                            color: Color(0xFF14181B),
                                            fontSize: 24.0,
                                            letterSpacing: 0.0,
                                            fontWeight: FontWeight.w500,
                                          ),
                                    ),
                                  ),
                                  Padding(
                                    padding: EdgeInsetsDirectional.fromSTEB(
                                        0.0, 4.0, 0.0, 0.0),
                                    child: ListView(
                                      padding: EdgeInsets.zero,
                                      shrinkWrap: true,
                                      scrollDirection: Axis.vertical,
                                      children: [
                                        Padding(
                                          padding:
                                              EdgeInsetsDirectional.fromSTEB(
                                                  30.0, 12.0, 16.0, 12.0),
                                          child: Column(
                                            mainAxisSize: MainAxisSize.max,
                                            mainAxisAlignment:
                                                MainAxisAlignment.center,
                                            crossAxisAlignment:
                                                CrossAxisAlignment.start,
                                            children: [
                                              Row(
                                                mainAxisSize: MainAxisSize.max,
                                                mainAxisAlignment:
                                                    MainAxisAlignment
                                                        .spaceBetween,
                                                children: [
                                                  Text(
                                                    (recentSessions.isEmpty)
                                                        ? 'No Previous Session'
                                                        : 'Last Session (10/20/25)',
                                                    style: FlutterFlowTheme.of(
                                                            context)
                                                        .bodySmall
                                                        .override(
                                                          fontFamily:
                                                              'Plus Jakarta Sans',
                                                          color:
                                                              Color(0xFF14181B),
                                                          fontSize: 18.0,
                                                          letterSpacing: 0.0,
                                                          fontWeight:
                                                              FontWeight.normal,
                                                        ),
                                                  ),
                                                ],
                                              ),
                                              Padding(
                                                padding: EdgeInsetsDirectional
                                                    .fromSTEB(
                                                        0.0, 4.0, 0.0, 0.0),
                                                child: Text(
                                                  (recentSessions.isEmpty)
                                                      ? 'Session time:\nRed lights ran:\nStop signs missed:\nSpeed limit violations:\nTurning signals missed:'
                                                      : "Session time: ${recentSessions.last['sessionTime']}\nRed lights ran: ${recentSessions.last['lightsRan']}\nStop signs missed: ${recentSessions.last['stopSignsMissed']}\nSpeed limit violations: ${recentSessions.last['speedViolations']}\nTurning signals missed: ${recentSessions.last['turnSignalsMissed']}",
                                                  style: FlutterFlowTheme.of(
                                                          context)
                                                      .bodyMedium
                                                      .override(
                                                        fontFamily:
                                                            'Plus Jakarta Sans',
                                                        color:
                                                            Color(0xFF14181B),
                                                        fontSize: 14.0,
                                                        letterSpacing: 0.0,
                                                        fontWeight:
                                                            FontWeight.normal,
                                                      ),
                                                ),
                                              ),
                                              Padding(
                                                padding: EdgeInsetsDirectional
                                                    .fromSTEB(
                                                        0.0, 8.0, 0.0, 0.0),
                                                child: Row(
                                                  mainAxisSize:
                                                      MainAxisSize.max,
                                                  children: [
                                                    Padding(
                                                      padding:
                                                          EdgeInsetsDirectional
                                                              .fromSTEB(
                                                                  0.0,
                                                                  0.0,
                                                                  4.0,
                                                                  0.0),
                                                      child: Text(
                                                        'Score:',
                                                        style: FlutterFlowTheme
                                                                .of(context)
                                                            .labelMedium
                                                            .override(
                                                              fontFamily:
                                                                  'Plus Jakarta Sans',
                                                              color: Color(
                                                                  0xFF57636C),
                                                              fontSize: 18.0,
                                                              letterSpacing:
                                                                  0.0,
                                                              fontWeight:
                                                                  FontWeight
                                                                      .normal,
                                                            ),
                                                      ),
                                                    ),
                                                    Expanded(
                                                      child: Text(
                                                        (recentSessions.isEmpty)
                                                            ? 'null'
                                                            : "${recentSessions.last['score']}",
                                                        style: FlutterFlowTheme
                                                                .of(context)
                                                            .bodyMedium
                                                            .override(
                                                              fontFamily:
                                                                  'Plus Jakarta Sans',
                                                              color: Color(
                                                                  0xFF14181B),
                                                              fontSize: 18.0,
                                                              letterSpacing:
                                                                  0.0,
                                                              fontWeight:
                                                                  FontWeight
                                                                      .normal,
                                                            ),
                                                      ),
                                                    ),
                                                  ],
                                                ),
                                              ),
                                            ],
                                          ),
                                        ),
                                      ],
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          ),
                        ),
                      ),
                      Padding(
                        padding: EdgeInsetsDirectional.fromSTEB(
                            16.0, 0.0, 16.0, 0.0),
                        child: Container(
                          width: MediaQuery.sizeOf(context).width * 1.0,
                          decoration: BoxDecoration(
                            color: Colors.white,
                            boxShadow: [
                              BoxShadow(
                                blurRadius: 4.0,
                                color: Color(0x33000000),
                                offset: Offset(
                                  0.0,
                                  2.0,
                                ),
                              )
                            ],
                            borderRadius: BorderRadius.circular(12.0),
                          ),
                          child: Align(
                            alignment: AlignmentDirectional(0.0, 0.0),
                            child: Column(
                              mainAxisSize: MainAxisSize.max,
                              children: [
                                Align(
                                  alignment: AlignmentDirectional(-1.0, 0.0),
                                  child: Padding(
                                    padding: EdgeInsetsDirectional.fromSTEB(
                                        16.0, 10.0, 0.0, 4.0),
                                    child: Text(
                                      'Your Driving Statistics',
                                      style: FlutterFlowTheme.of(context)
                                          .headlineMedium
                                          .override(
                                            fontFamily: 'Outfit',
                                            color: Color(0xFF14181B),
                                            fontSize: 24.0,
                                            letterSpacing: 0.0,
                                            fontWeight: FontWeight.w600,
                                          ),
                                    ),
                                  ),
                                ),
                                Column(
                                  // padding: EdgeInsets.zero,
                                  // shrinkWrap: true,
                                  // scrollDirection: Axis.vertical,
                                  children: [
                                    Column(
                                      mainAxisSize: MainAxisSize.max,
                                      children: [
                                        Align(
                                          alignment:
                                              AlignmentDirectional(0.0, 1.0),
                                          child: Padding(
                                            padding:
                                                EdgeInsetsDirectional.fromSTEB(
                                                    0.0, 15.0, 0.0, 0.0),
                                            child: Text(
                                              'Score Performance',
                                              style:
                                                  FlutterFlowTheme.of(context)
                                                      .bodyMedium
                                                      .override(
                                                        fontFamily: 'Inter',
                                                        fontSize: 18.0,
                                                        letterSpacing: 0.0,
                                                      ),
                                            ),
                                          ),
                                        ),
                                        Padding(
                                          padding:
                                              EdgeInsetsDirectional.fromSTEB(
                                                  16.0, 0.0, 16.0, 0.0),
                                          child: Stack(
                                            children: [
                                              Container(
                                                width: double.infinity,
                                                height: 200.0,
                                                child: FlutterFlowLineChart(
                                                  data: [
                                                    FFLineChartData(
                                                      xData: scoreXData,
                                                      yData: scoreYData,
                                                      settings:
                                                          LineChartBarData(
                                                        color:
                                                            Color(0xFF4B39EF),
                                                        barWidth: 2.0,
                                                        isCurved: true,
                                                        preventCurveOverShooting:
                                                            true,
                                                        dotData: FlDotData(
                                                            show: false),
                                                        belowBarData:
                                                            BarAreaData(
                                                          show: true,
                                                          color:
                                                              Color(0x4C4B39EF),
                                                        ),
                                                      ),
                                                    )
                                                  ],
                                                  chartStylingInfo:
                                                      ChartStylingInfo(
                                                    enableTooltip: true,
                                                    backgroundColor:
                                                        Colors.white,
                                                    showBorder: false,
                                                  ),
                                                  //axisBounds: AxisBounds(),
                                                  axisBounds: AxisBounds(
                                                    minY: 70,
                                                    maxY: 100,
                                                  ),
                                                  xAxisLabelInfo: AxisLabelInfo(
                                                    title: 'Last 30 Sessions',
                                                    titleTextStyle:
                                                        FlutterFlowTheme.of(
                                                                context)
                                                            .bodyMedium
                                                            .override(
                                                              fontFamily:
                                                                  'Plus Jakarta Sans',
                                                              color: Color(
                                                                  0xFF14181B),
                                                              fontSize: 14.0,
                                                              letterSpacing:
                                                                  0.0,
                                                              fontWeight:
                                                                  FontWeight
                                                                      .normal,
                                                            ),
                                                  ),
                                                  yAxisLabelInfo: AxisLabelInfo(
                                                    title: 'Score',
                                                    titleTextStyle:
                                                        FlutterFlowTheme.of(
                                                                context)
                                                            .bodyMedium
                                                            .override(
                                                              fontFamily:
                                                                  'Plus Jakarta Sans',
                                                              color: Color(
                                                                  0xFF14181B),
                                                              fontSize: 14.0,
                                                              letterSpacing:
                                                                  0.0,
                                                              fontWeight:
                                                                  FontWeight
                                                                      .normal,
                                                            ),
                                                    labelTextStyle:
                                                        FlutterFlowTheme.of(
                                                                context)
                                                            .bodyMedium
                                                            .override(
                                                              fontFamily:
                                                                  'Plus Jakarta Sans',
                                                              fontSize:
                                                                  10.0, // make tick labels smaller
                                                            ),
                                                    showLabels: true,
                                                    labelInterval:
                                                        10, // show label every 10
                                                    labelFormatter:
                                                        LabelFormatter(
                                                      numberFormat:
                                                          (double val) => val
                                                              .toInt()
                                                              .toString(),
                                                    ), // display integer
                                                  ),
                                                ),
                                              ),
                                              Positioned(
                                                left: 47.0,
                                                child: Container(
                                                  width: 100,
                                                  height: 175.0,
                                                  decoration: BoxDecoration(
                                                      border: Border(
                                                    left: BorderSide(
                                                      color: Color(0xFFE0E3E7),
                                                      width: 1.0,
                                                    ),
                                                    bottom: BorderSide(
                                                      color: Color(0xFFE0E3E7),
                                                      width: 1.0,
                                                    ),
                                                  )),
                                                ),
                                              )
                                            ],
                                          ),
                                        ),
                                      ],
                                    ),
                                    Divider(
                                        thickness: 1,
                                        indent: 25,
                                        endIndent: 25),
                                    Column(
                                      mainAxisSize: MainAxisSize.max,
                                      children: [
                                        Align(
                                          alignment:
                                              AlignmentDirectional(0.0, 1.0),
                                          child: Padding(
                                            padding:
                                                EdgeInsetsDirectional.fromSTEB(
                                                    0.0, 15.0, 0.0, 0.0),
                                            child: Text(
                                              'Red Lights Ran',
                                              style:
                                                  FlutterFlowTheme.of(context)
                                                      .bodyMedium
                                                      .override(
                                                        fontFamily: 'Inter',
                                                        fontSize: 18.0,
                                                        letterSpacing: 0.0,
                                                      ),
                                            ),
                                          ),
                                        ),
                                        Padding(
                                            padding:
                                                EdgeInsetsDirectional.fromSTEB(
                                                    16.0, 0.0, 16.0, 0.0),
                                            child: Stack(
                                              children: [
                                                Container(
                                                  width: double.infinity,
                                                  height: 200.0,
                                                  child: FlutterFlowLineChart(
                                                    data: [
                                                      FFLineChartData(
                                                        xData: redLightsXData,
                                                        yData: redLightsYData,
                                                        settings:
                                                            LineChartBarData(
                                                          color:
                                                              Color(0xFF4B39EF),
                                                          barWidth: 2.0,
                                                          isCurved: true,
                                                          preventCurveOverShooting:
                                                              true,
                                                          dotData: FlDotData(
                                                              show: false),
                                                          belowBarData:
                                                              BarAreaData(
                                                            show: true,
                                                            color: Color(
                                                                0x4C4B39EF),
                                                          ),
                                                        ),
                                                      )
                                                    ],
                                                    chartStylingInfo:
                                                        ChartStylingInfo(
                                                      enableTooltip: true,
                                                      backgroundColor:
                                                          Colors.white,
                                                      showBorder: false,
                                                    ),
                                                    //axisBounds: AxisBounds(),
                                                    axisBounds: AxisBounds(
                                                      minY: 0,
                                                      maxY: 5,
                                                    ),
                                                    xAxisLabelInfo:
                                                        AxisLabelInfo(
                                                      title: 'Last 30 Sessions',
                                                      titleTextStyle:
                                                          FlutterFlowTheme.of(
                                                                  context)
                                                              .bodyMedium
                                                              .override(
                                                                fontFamily:
                                                                    'Plus Jakarta Sans',
                                                                color: Color(
                                                                    0xFF14181B),
                                                                fontSize: 14.0,
                                                                letterSpacing:
                                                                    0.0,
                                                                fontWeight:
                                                                    FontWeight
                                                                        .normal,
                                                              ),
                                                    ),
                                                    yAxisLabelInfo:
                                                        AxisLabelInfo(
                                                      title: 'Violations',
                                                      titleTextStyle:
                                                          FlutterFlowTheme.of(
                                                                  context)
                                                              .bodyMedium
                                                              .override(
                                                                fontFamily:
                                                                    'Plus Jakarta Sans',
                                                                color: Color(
                                                                    0xFF14181B),
                                                                fontSize: 14.0,
                                                                letterSpacing:
                                                                    0.0,
                                                                fontWeight:
                                                                    FontWeight
                                                                        .normal,
                                                              ),
                                                      showLabels: true,
                                                      labelInterval:
                                                          1, // show label every 10
                                                      labelFormatter:
                                                          LabelFormatter(
                                                        numberFormat:
                                                            (double val) => val
                                                                .toInt()
                                                                .toString(),
                                                      ), // display integer
                                                    ),
                                                  ),
                                                ),
                                                Positioned(
                                                  left: 47.0,
                                                  child: Container(
                                                    width: 100,
                                                    height: 175.0,
                                                    decoration: BoxDecoration(
                                                        border: Border(
                                                      left: BorderSide(
                                                        color:
                                                            Color(0xFFE0E3E7),
                                                        width: 1.0,
                                                      ),
                                                      bottom: BorderSide(
                                                        color:
                                                            Color(0xFFE0E3E7),
                                                        width: 1.0,
                                                      ),
                                                    )),
                                                  ),
                                                )
                                              ],
                                            )),
                                      ],
                                    ),
                                    Divider(
                                        thickness: 1,
                                        indent: 25,
                                        endIndent: 25),
                                    Column(
                                      mainAxisSize: MainAxisSize.max,
                                      children: [
                                        Align(
                                          alignment:
                                              AlignmentDirectional(0.0, 1.0),
                                          child: Padding(
                                            padding:
                                                EdgeInsetsDirectional.fromSTEB(
                                                    0.0, 15.0, 0.0, 0.0),
                                            child: Text(
                                              'Stop Signs Missed',
                                              style:
                                                  FlutterFlowTheme.of(context)
                                                      .bodyMedium
                                                      .override(
                                                        fontFamily: 'Inter',
                                                        fontSize: 18.0,
                                                        letterSpacing: 0.0,
                                                      ),
                                            ),
                                          ),
                                        ),
                                        Padding(
                                            padding:
                                                EdgeInsetsDirectional.fromSTEB(
                                                    16.0, 0.0, 16.0, 0.0),
                                            child: Stack(
                                              children: [
                                                Container(
                                                  width: double.infinity,
                                                  height: 200.0,
                                                  child: FlutterFlowLineChart(
                                                    data: [
                                                      FFLineChartData(
                                                        xData: stopSignsXData,
                                                        yData: stopSignsYData,
                                                        settings:
                                                            LineChartBarData(
                                                          color:
                                                              Color(0xFF4B39EF),
                                                          barWidth: 2.0,
                                                          isCurved: true,
                                                          preventCurveOverShooting:
                                                              true,
                                                          dotData: FlDotData(
                                                              show: false),
                                                          belowBarData:
                                                              BarAreaData(
                                                            show: true,
                                                            color: Color(
                                                                0x4C4B39EF),
                                                          ),
                                                        ),
                                                      )
                                                    ],
                                                    chartStylingInfo:
                                                        ChartStylingInfo(
                                                      enableTooltip: true,
                                                      backgroundColor:
                                                          Colors.white,
                                                      showBorder: false,
                                                    ),
                                                    //axisBounds: AxisBounds(),
                                                    axisBounds: AxisBounds(
                                                      minY: 0,
                                                      maxY: 5,
                                                    ),
                                                    xAxisLabelInfo:
                                                        AxisLabelInfo(
                                                      title: 'Last 30 Sessions',
                                                      titleTextStyle:
                                                          FlutterFlowTheme.of(
                                                                  context)
                                                              .bodyMedium
                                                              .override(
                                                                fontFamily:
                                                                    'Plus Jakarta Sans',
                                                                color: Color(
                                                                    0xFF14181B),
                                                                fontSize: 14.0,
                                                                letterSpacing:
                                                                    0.0,
                                                                fontWeight:
                                                                    FontWeight
                                                                        .normal,
                                                              ),
                                                    ),
                                                    yAxisLabelInfo:
                                                        AxisLabelInfo(
                                                      title: 'Violations',
                                                      titleTextStyle:
                                                          FlutterFlowTheme.of(
                                                                  context)
                                                              .bodyMedium
                                                              .override(
                                                                fontFamily:
                                                                    'Plus Jakarta Sans',
                                                                color: Color(
                                                                    0xFF14181B),
                                                                fontSize: 14.0,
                                                                letterSpacing:
                                                                    0.0,
                                                                fontWeight:
                                                                    FontWeight
                                                                        .normal,
                                                              ),
                                                      showLabels: true,
                                                      labelInterval:
                                                          1, // show label every 10
                                                      labelFormatter:
                                                          LabelFormatter(
                                                        numberFormat:
                                                            (double val) => val
                                                                .toInt()
                                                                .toString(),
                                                      ), //
                                                    ),
                                                  ),
                                                ),
                                                Positioned(
                                                  left: 47.0,
                                                  child: Container(
                                                    width: 100,
                                                    height: 175.0,
                                                    decoration: BoxDecoration(
                                                        border: Border(
                                                      left: BorderSide(
                                                        color:
                                                            Color(0xFFE0E3E7),
                                                        width: 1.0,
                                                      ),
                                                      bottom: BorderSide(
                                                        color:
                                                            Color(0xFFE0E3E7),
                                                        width: 1.0,
                                                      ),
                                                    )),
                                                  ),
                                                )
                                              ],
                                            )),
                                      ],
                                    ),
                                    Divider(
                                        thickness: 1,
                                        indent: 25,
                                        endIndent: 25),
                                    Column(
                                      mainAxisSize: MainAxisSize.max,
                                      children: [
                                        Align(
                                          alignment:
                                              AlignmentDirectional(0.0, 1.0),
                                          child: Padding(
                                            padding:
                                                EdgeInsetsDirectional.fromSTEB(
                                                    0.0, 15.0, 0.0, 0.0),
                                            child: Text(
                                              'Speed Limit Violations',
                                              style:
                                                  FlutterFlowTheme.of(context)
                                                      .bodyMedium
                                                      .override(
                                                        fontFamily: 'Inter',
                                                        fontSize: 18.0,
                                                        letterSpacing: 0.0,
                                                      ),
                                            ),
                                          ),
                                        ),
                                        Padding(
                                            padding:
                                                EdgeInsetsDirectional.fromSTEB(
                                                    16.0, 0.0, 16.0, 0.0),
                                            child: Stack(
                                              children: [
                                                Container(
                                                  width: double.infinity,
                                                  height: 200.0,
                                                  child: FlutterFlowLineChart(
                                                    data: [
                                                      FFLineChartData(
                                                        xData: speedingXData,
                                                        yData: speedingYData,
                                                        settings:
                                                            LineChartBarData(
                                                          color:
                                                              Color(0xFF4B39EF),
                                                          barWidth: 2.0,
                                                          isCurved: true,
                                                          preventCurveOverShooting:
                                                              true,
                                                          dotData: FlDotData(
                                                              show: false),
                                                          belowBarData:
                                                              BarAreaData(
                                                            show: true,
                                                            color: Color(
                                                                0x4C4B39EF),
                                                          ),
                                                        ),
                                                      )
                                                    ],
                                                    chartStylingInfo:
                                                        ChartStylingInfo(
                                                      enableTooltip: true,
                                                      backgroundColor:
                                                          Colors.white,
                                                      showBorder: false,
                                                    ),
                                                    //axisBounds: AxisBounds(),
                                                    axisBounds: AxisBounds(
                                                      minY: 0,
                                                      maxY: 5,
                                                    ),
                                                    xAxisLabelInfo:
                                                        AxisLabelInfo(
                                                      title: 'Last 30 Sessions',
                                                      titleTextStyle:
                                                          FlutterFlowTheme.of(
                                                                  context)
                                                              .bodyMedium
                                                              .override(
                                                                fontFamily:
                                                                    'Plus Jakarta Sans',
                                                                color: Color(
                                                                    0xFF14181B),
                                                                fontSize: 14.0,
                                                                letterSpacing:
                                                                    0.0,
                                                                fontWeight:
                                                                    FontWeight
                                                                        .normal,
                                                              ),
                                                    ),
                                                    yAxisLabelInfo:
                                                        AxisLabelInfo(
                                                      title: 'Violations',
                                                      titleTextStyle:
                                                          FlutterFlowTheme.of(
                                                                  context)
                                                              .bodyMedium
                                                              .override(
                                                                fontFamily:
                                                                    'Plus Jakarta Sans',
                                                                color: Color(
                                                                    0xFF14181B),
                                                                fontSize: 14.0,
                                                                letterSpacing:
                                                                    0.0,
                                                                fontWeight:
                                                                    FontWeight
                                                                        .normal,
                                                              ),
                                                      showLabels: true,
                                                      labelInterval:
                                                          1, // show label every 10
                                                      labelFormatter:
                                                          LabelFormatter(
                                                        numberFormat:
                                                            (double val) => val
                                                                .toInt()
                                                                .toString(),
                                                      ), //
                                                    ),
                                                  ),
                                                ),
                                                Positioned(
                                                  left: 47.0,
                                                  child: Container(
                                                    width: 100,
                                                    height: 175.0,
                                                    decoration: BoxDecoration(
                                                        border: Border(
                                                      left: BorderSide(
                                                        color:
                                                            Color(0xFFE0E3E7),
                                                        width: 1.0,
                                                      ),
                                                      bottom: BorderSide(
                                                        color:
                                                            Color(0xFFE0E3E7),
                                                        width: 1.0,
                                                      ),
                                                    )),
                                                  ),
                                                )
                                              ],
                                            )),
                                      ],
                                    ),
                                    Divider(
                                        thickness: 1,
                                        indent: 25,
                                        endIndent: 25),
                                    Column(
                                      mainAxisSize: MainAxisSize.max,
                                      children: [
                                        Align(
                                          alignment:
                                              AlignmentDirectional(0.0, 1.0),
                                          child: Padding(
                                            padding:
                                                EdgeInsetsDirectional.fromSTEB(
                                                    0.0, 15.0, 0.0, 0.0),
                                            child: Text(
                                              'Turning Signals Missed',
                                              style:
                                                  FlutterFlowTheme.of(context)
                                                      .bodyMedium
                                                      .override(
                                                        fontFamily: 'Inter',
                                                        fontSize: 18.0,
                                                        letterSpacing: 0.0,
                                                      ),
                                            ),
                                          ),
                                        ),
                                        Padding(
                                            padding:
                                                EdgeInsetsDirectional.fromSTEB(
                                                    16.0, 0.0, 16.0, 0.0),
                                            child: Stack(
                                              children: [
                                                Container(
                                                  width: double.infinity,
                                                  height: 200.0,
                                                  child: FlutterFlowLineChart(
                                                    data: [
                                                      FFLineChartData(
                                                        xData: turningXData,
                                                        yData: turningYData,
                                                        settings:
                                                            LineChartBarData(
                                                          color:
                                                              Color(0xFF4B39EF),
                                                          barWidth: 2.0,
                                                          isCurved: true,
                                                          preventCurveOverShooting:
                                                              true,
                                                          dotData: FlDotData(
                                                              show: false),
                                                          belowBarData:
                                                              BarAreaData(
                                                            show: true,
                                                            color: Color(
                                                                0x4C4B39EF),
                                                          ),
                                                        ),
                                                      )
                                                    ],
                                                    chartStylingInfo:
                                                        ChartStylingInfo(
                                                      enableTooltip: true,
                                                      backgroundColor:
                                                          Colors.white,
                                                      showBorder: false,
                                                    ),
                                                    //axisBounds: AxisBounds(),
                                                    axisBounds: AxisBounds(
                                                      minY: 0,
                                                      maxY: 5,
                                                    ),
                                                    xAxisLabelInfo:
                                                        AxisLabelInfo(
                                                      title: 'Last 30 Sessions',
                                                      titleTextStyle:
                                                          FlutterFlowTheme.of(
                                                                  context)
                                                              .bodyMedium
                                                              .override(
                                                                fontFamily:
                                                                    'Plus Jakarta Sans',
                                                                color: Color(
                                                                    0xFF14181B),
                                                                fontSize: 14.0,
                                                                letterSpacing:
                                                                    0.0,
                                                                fontWeight:
                                                                    FontWeight
                                                                        .normal,
                                                              ),
                                                    ),
                                                    yAxisLabelInfo:
                                                        AxisLabelInfo(
                                                      title: 'Violations',
                                                      titleTextStyle:
                                                          FlutterFlowTheme.of(
                                                                  context)
                                                              .bodyMedium
                                                              .override(
                                                                fontFamily:
                                                                    'Plus Jakarta Sans',
                                                                color: Color(
                                                                    0xFF14181B),
                                                                fontSize: 14.0,
                                                                letterSpacing:
                                                                    0.0,
                                                                fontWeight:
                                                                    FontWeight
                                                                        .normal,
                                                              ),
                                                      showLabels: true,
                                                      labelInterval:
                                                          1, // show label every 10
                                                      labelFormatter:
                                                          LabelFormatter(
                                                        numberFormat:
                                                            (double val) => val
                                                                .toInt()
                                                                .toString(),
                                                      ), //
                                                    ),
                                                  ),
                                                ),
                                                Positioned(
                                                  left: 47.0,
                                                  child: Container(
                                                    width: 100,
                                                    height: 175.0,
                                                    decoration: BoxDecoration(
                                                        border: Border(
                                                      left: BorderSide(
                                                        color:
                                                            Color(0xFFE0E3E7),
                                                        width: 1.0,
                                                      ),
                                                      bottom: BorderSide(
                                                        color:
                                                            Color(0xFFE0E3E7),
                                                        width: 1.0,
                                                      ),
                                                    )),
                                                  ),
                                                )
                                              ],
                                            )),
                                        // Padding(
                                        //   padding: EdgeInsetsDirectional.fromSTEB(
                                        //       16.0, 0.0, 16.0, 0.0),
                                        //   child: Container(
                                        //     width: double.infinity,
                                        //     height: 200.0,
                                        //     child: FlutterFlowLineChart(
                                        //       data: [
                                        //         FFLineChartData(
                                        //           xData: List.generate(
                                        //               random_data.randomInteger(5, 5),
                                        //               (index) => random_data
                                        //                   .randomInteger(0, 10)),
                                        //           yData: List.generate(
                                        //               random_data.randomInteger(5, 5),
                                        //               (index) => random_data
                                        //                   .randomInteger(0, 10)),
                                        //           settings: LineChartBarData(
                                        //             color: Color(0xFF4B39EF),
                                        //             barWidth: 2.0,
                                        //             isCurved: true,
                                        //             preventCurveOverShooting: true,
                                        //             dotData: FlDotData(show: false),
                                        //             belowBarData: BarAreaData(
                                        //               show: true,
                                        //               color: Color(0x4C4B39EF),
                                        //             ),
                                        //           ),
                                        //         )
                                        //       ],
                                        //       chartStylingInfo: ChartStylingInfo(
                                        //         enableTooltip: true,
                                        //         backgroundColor: Colors.white,
                                        //         showBorder: false,
                                        //       ),
                                        //       axisBounds: AxisBounds(),
                                        //       xAxisLabelInfo: AxisLabelInfo(
                                        //         title: 'Last x Days',
                                        //         titleTextStyle: FlutterFlowTheme.of(
                                        //                 context)
                                        //             .bodyMedium
                                        //             .override(
                                        //               fontFamily: 'Plus Jakarta Sans',
                                        //               color: Color(0xFF14181B),
                                        //               fontSize: 14.0,
                                        //               letterSpacing: 0.0,
                                        //               fontWeight: FontWeight.normal,
                                        //             ),
                                        //       ),
                                        //       yAxisLabelInfo: AxisLabelInfo(
                                        //         title: 'Score',
                                        //         titleTextStyle: FlutterFlowTheme.of(
                                        //                 context)
                                        //             .bodyMedium
                                        //             .override(
                                        //               fontFamily: 'Plus Jakarta Sans',
                                        //               color: Color(0xFF14181B),
                                        //               fontSize: 14.0,
                                        //               letterSpacing: 0.0,
                                        //               fontWeight: FontWeight.normal,
                                        //             ),
                                        //       ),
                                        //     ),
                                        //   ),
                                        // ),
                                      ],
                                    ),
                                  ],
                                ),
                              ],
                            ),
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
